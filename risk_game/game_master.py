from typing import Any, Dict, List, Optional, Tuple
import random
import pandas as pd
import time
from risk_game.player_agent import PlayerAgent
from risk_game.game_state import GameState
from risk_game.rules import Rules
from risk_game.card_deck import Deck, Card
from risk_game.utils.decorators import track_turn_time
from risk_game.utils.game_admin import create_game_folder, save_game_state, \
save_player_data, save_end_game_results, save_turn_summary, \
build_llm_interaction_logger, save_game_manifest
from risk_game.paths import get_game_results_dir
from risk_game.utils.turn_summary import (
    build_player_model_info,
    build_turn_outcome,
    snapshot_all_players,
    snapshot_player_state,
)


class GameMaster:
    def __init__(self, rules: Rules)-> None:
        self.players: List[PlayerAgent] = []
        self.dead_players: List[PlayerAgent] = []
        self.active_players: List[PlayerAgent] = []
        self.game_state = None
        self.game_over = False
        self.game_round = 0
        self.phase: int = 0
        self.current_player_index = -1
        self.deck = None
        self.winner: Optional[PlayerAgent] = None
        self.discarded_cards = []
        self.rules = rules  # Store the rules instance
        self.player_cards: Dict[str, List[Card]] = {}
        self.victory_condition: Optional[str] = None
        self.current_turn_trace: Optional[Dict[str, Any]] = None
        self.last_completed_turn_trace: Optional[Dict[str, Any]] = None
        self.turn_summaries: List[Dict[str, Any]] = []
        self._turn_trace_start_wallclock: float = 0.0
        self.llm_interaction_logger = None

    def __repr__(self) -> str:
        return (f"<GameMaster("
                f"game_round={self.game_round}, "
                f"phase={self.phase}, "
                f"active_players={len(self.active_players)}, "
                f"dead_players={len(self.dead_players)}, "
                f"current_player={self.players[self.current_player_index].name if self.current_player_index != -1 else 'None'}, "
                f"winner={self.winner.name if self.winner else 'None'}, "
                f"game_over={self.game_over}, "
                f"victory_condition={self.victory_condition or 'None'}, "
                f"rules={self.rules})>"
                )



    def add_player(
        self,
        name: str,
        llm_client: 'LLMClient',
        planning_llm_client: Optional['LLMClient'] = None,
        runtime_overrides: Optional[Dict[str, Any]] = None,
    ) -> None:
        if len(self.players) >= 6:
            raise ValueError("Cannot add more than 6 players")
        player = PlayerAgent(name, llm_client, planning_llm_client=planning_llm_client)
        player.runtime_overrides = {
            key: value
            for key, value in (runtime_overrides or {}).items()
            if value is not None
        }
        self._apply_runtime_settings_to_player(player)
        self.players.append(player)
        self.player_cards[name] = []  # Initialize an empty list of cards 

    def _runtime_value(
        self,
        player: "PlayerAgent",
        key: str,
        default: Any,
    ) -> Any:
        return player.runtime_overrides.get(key, default)

    def _find_player_by_name(self, player_name: Optional[str]) -> Optional[PlayerAgent]:
        if player_name is None:
            return None
        return next((player for player in self.players if player.name == player_name), None)

    def _format_console_player_label(self, player_name: Optional[str]) -> str:
        if player_name is None:
            return "Unknown"
        player = self._find_player_by_name(player_name)
        if player is None:
            return player_name
        provider = getattr(player.llm_client, "provider_name", None)
        model = getattr(player.llm_client, "model_type", None)
        if provider and model:
            return f"{player_name} [{provider}:{model}]"
        if model:
            return f"{player_name} [{model}]"
        return player_name

    def _format_console_client_label(
        self,
        player: PlayerAgent,
        *,
        planning: bool = False,
    ) -> str:
        llm_client = (
            player.planning_llm_client
            if planning and player.planning_llm_client is not None
            else player.llm_client
        )
        provider = getattr(llm_client, "provider_name", None)
        model = getattr(llm_client, "model_type", None)
        if provider and model:
            return f"{provider}:{model}"
        return str(model or provider or "unknown")

    def _format_remaining_turn_time_for_console(
        self,
        player: PlayerAgent,
    ) -> str:
        remaining = player.remaining_turn_time_seconds()
        if remaining is None:
            return "unbounded"
        return f"{remaining:.1f}s"

    def _print_phase_completion(
        self,
        *,
        player: PlayerAgent,
        completed_phase: str,
        elapsed_seconds: float,
        next_phase: Optional[str] = None,
        planning: bool = False,
        include_plan: bool = False,
        extra_detail: Optional[str] = None,
    ) -> None:
        parts = [
            f"{player.name} completed {completed_phase} via "
            f"{self._format_console_client_label(player, planning=planning)}",
            f"spent {elapsed_seconds:.1f}s",
        ]
        if include_plan:
            plan_text = (player.turn_strategy or "No explicit plan.").replace("\n", " ")
            parts.append(f"plan: {plan_text[:220]}")
        if not planning:
            parts.append(
                "remaining execution time "
                f"{self._format_remaining_turn_time_for_console(player)}"
            )
        if extra_detail:
            parts.append(extra_detail)
        if next_phase:
            parts.append(f"starting {next_phase}")
        print(" | ".join(parts))

    def _print_attack_console_line(
        self,
        player: PlayerAgent,
        from_territory: Optional[str],
        target_territory: Optional[str],
        committed_troops: Optional[int],
    ) -> None:
        if (
            from_territory in (None, "Blank")
            or target_territory in (None, "Blank")
            or committed_troops in (None, 0)
        ):
            return

        attacker_total_troops = self.game_state.check_number_of_troops(
            player.name, from_territory
        )
        defender_control = self.game_state.get_territory_control(target_territory)
        defender_name = None
        defender_troops = 0
        if defender_control is not None:
            defender_name, defender_troops = defender_control

        print(
            "ATTACK: "
            f"{self._format_console_player_label(player.name)} attacks "
            f"{self._format_console_player_label(defender_name)} | "
            f"{from_territory} ({attacker_total_troops}) -> "
            f"{target_territory} ({defender_troops}) | "
            f"commits {committed_troops} troop(s)"
        )

    def _print_attack_outcome_console_line(
        self,
        *,
        player: PlayerAgent,
        defender_name: Optional[str],
        target_territory: Optional[str],
        outcome: str,
    ) -> None:
        if target_territory in (None, "Blank") or outcome == "no_attack":
            return

        if outcome == "win":
            occupying_troops = self.game_state.check_number_of_troops(
                player.name, target_territory
            )
            print(
                "ATTACK RESULT: "
                f"{self._format_console_player_label(player.name)} captured "
                f"{target_territory} from "
                f"{self._format_console_player_label(defender_name)} | "
                f"occupying troops: {occupying_troops}"
            )
            return

        if defender_name is None:
            return

        remaining_defender_troops = self.game_state.check_number_of_troops(
            defender_name, target_territory
        )
        print(
            "ATTACK RESULT: "
            f"{self._format_console_player_label(defender_name)} held "
            f"{target_territory} against "
            f"{self._format_console_player_label(player.name)} | "
            f"remaining defenders: {remaining_defender_troops}"
        )

    def _apply_runtime_settings_to_player(self, player: "PlayerAgent") -> None:
        player.turn_time_limit_seconds = self._runtime_value(
            player,
            "turn_time_limit_seconds",
            self.rules.turn_time_limit_seconds,
        )
        player.planning_time_limit_seconds = self._runtime_value(
            player,
            "planning_time_limit_seconds",
            self.rules.planning_time_limit_seconds,
        )
        player.placement_time_limit_seconds = self._runtime_value(
            player,
            "placement_time_limit_seconds",
            self.rules.placement_time_limit_seconds,
        )
        player.placement_reasoning_effort = self._runtime_value(
            player,
            "placement_reasoning_effort",
            self.rules.placement_reasoning_effort,
        )
        player.planning_reasoning_effort = self._runtime_value(
            player,
            "planning_reasoning_effort",
            self.rules.planning_reasoning_effort,
        )
        player.attack_reasoning_effort = self._runtime_value(
            player,
            "attack_reasoning_effort",
            self.rules.attack_reasoning_effort,
        )
        player.fortify_reasoning_effort = self._runtime_value(
            player,
            "fortify_reasoning_effort",
            self.rules.fortify_reasoning_effort,
        )
        player.card_trade_reasoning_effort = self._runtime_value(
            player,
            "card_trade_reasoning_effort",
            self.rules.card_trade_reasoning_effort,
        )
        player.configure_llm_interaction_logger(self.llm_interaction_logger)

    def _build_turn_event(
        self,
        player: "PlayerAgent",
        phase: str,
        attempt: int,
        reasoning: Optional[str],
        valid: bool,
        error: Optional[str],
        **extra: Any,
    ) -> Dict[str, Any]:
        latest_decision = player.get_latest_turn_decision()
        raw_response = None
        interaction_index = None
        llm_used_fallback_response = False
        llm_error = None
        llm_error_type = None
        llm_timeout_seconds = None
        llm_decision_time_seconds = None
        if latest_decision and latest_decision.get("phase") == phase:
            raw_response = latest_decision.get("raw_response")
            interaction_index = latest_decision.get("interaction_index")
            llm_used_fallback_response = bool(
                latest_decision.get("used_fallback_response")
            )
            llm_error = latest_decision.get("error")
            llm_error_type = latest_decision.get("error_type")
            llm_timeout_seconds = latest_decision.get("timeout_seconds")
            llm_decision_time_seconds = latest_decision.get("decision_time_seconds")

        event: Dict[str, Any] = {
            "phase": phase,
            "attempt": attempt,
            "valid": valid,
            "error": error,
            "reasoning": reasoning,
            "raw_response": raw_response,
            "fallback": False,
            "interaction_index": interaction_index,
            "llm_used_fallback_response": llm_used_fallback_response,
            "llm_error": llm_error,
            "llm_error_type": llm_error_type,
            "llm_timeout_seconds": llm_timeout_seconds,
            "llm_decision_time_seconds": llm_decision_time_seconds,
        }
        event.update(extra)
        return event

    def _record_turn_event(self, event: Dict[str, Any]) -> None:
        if self.current_turn_trace is None:
            return
        self.current_turn_trace["events"].append(event)

    def _start_turn_trace(self, player: "PlayerAgent") -> None:
        player.reset_turn_decision_log()
        self._turn_trace_start_wallclock = time.time()
        cards_before = len(self.player_cards.get(player.name, []))
        self.current_turn_trace = {
            "game_round": self.game_round,
            "player": build_player_model_info(player),
            "pre_turn": {
                "cards": cards_before,
                "player_state": snapshot_player_state(self.game_state, player.name),
                "all_players": snapshot_all_players(self.game_state),
            },
            "plan": {"text": "", "raw_response": None},
            "events": [],
        }

    def _capture_turn_plan(self, player: "PlayerAgent") -> None:
        if self.current_turn_trace is None:
            return
        latest_decision = player.get_latest_turn_decision()
        raw_response = None
        if latest_decision and latest_decision.get("phase") == "pre_turn_planning":
            raw_response = latest_decision.get("raw_response")
        self.current_turn_trace["plan"] = {
            "text": player.turn_strategy,
            "raw_response": raw_response,
        }

    def _finalize_turn_trace(
        self, player: "PlayerAgent", turn_number: Optional[int]
    ) -> Dict[str, Any]:
        if self.current_turn_trace is None:
            raise ValueError("Cannot finalize turn trace before starting one")

        cards_after = len(self.player_cards.get(player.name, []))
        post_turn_state = snapshot_player_state(self.game_state, player.name)
        turn_time_seconds = time.time() - self._turn_trace_start_wallclock
        resolved_turn_number = turn_number
        if resolved_turn_number is None:
            resolved_turn_number = len(self.turn_summaries) + 1
        self.current_turn_trace["turn_number"] = resolved_turn_number
        self.current_turn_trace["post_turn"] = {
            "cards": cards_after,
            "player_state": post_turn_state,
            "all_players": snapshot_all_players(self.game_state),
        }
        self.current_turn_trace["derived"] = build_turn_outcome(
            self.current_turn_trace["pre_turn"]["player_state"],
            post_turn_state,
            self.current_turn_trace["events"],
            cards_before=self.current_turn_trace["pre_turn"]["cards"],
            cards_after=cards_after,
            turn_time_seconds=turn_time_seconds,
        )
        self.current_turn_trace["derived"]["turn_timed_out"] = (
            player.turn_time_exhausted
        )
        self.current_turn_trace["llm_decisions"] = player.get_turn_decision_log()

        completed_trace = self.current_turn_trace
        self.last_completed_turn_trace = completed_trace
        self.turn_summaries.append(completed_trace)
        self.current_turn_trace = None
        return completed_trace

    def calculate_initial_troops(self, num_players: int) -> int:
        initial_troops_map = {2: 40,3: 35, 4: 30,5: 25,6: 20}
        return initial_troops_map[num_players]

    def init_game_state(self) -> None:
        num_players = len(self.players)
        # only init the game state if there are 2 or more players
        if num_players < 2:
            raise ValueError("Cannot start a game with fewer than 2 players")
        random.shuffle(self.players)
        intial_troops = self.calculate_initial_troops(num_players)
        for player in self.players:
            self._apply_runtime_settings_to_player(player)
            player.troops = intial_troops
        self.active_players = self.players.copy()
        self.game_state = GameState(self.active_players, self.rules)
        self.deck = Deck()

    def remove_player(self, player_name: str) -> None:
        player_to_remove = None
        remove_index = -1
        for i, player in enumerate(self.active_players):
            if player.name == player_name:
                player_to_remove = player
                remove_index = i
                break
        print(f"Index of Player to remove: {remove_index}")

        if player_to_remove:
            self.active_players.remove(player_to_remove)
            self.dead_players.append(player_to_remove)
            self.game_state.num_players = len(self.active_players)
            # Adjust current_player_index based on the removed player's position
            if remove_index < self.current_player_index:
                self.current_player_index -= 1
            elif remove_index == self.current_player_index:
                self.current_player_index = (
                    self.current_player_index % len(self.active_players)
                )
            # Reset current_player_index if it goes out of bounds
            if self.current_player_index >= len(self.active_players):
                self.current_player_index = 0
        else:
            print(f"{player_name} not found in active players")

    def list_players(self) -> None:
        for player in self.players:
            print(f"Name: {player.name}")

    def validate_single_move(
        self, player: 'PlayerAgent', 
        move: Tuple[Optional[str], Optional[int], Optional[str]]
        ) -> bool:
        territory, num_troops, _ = move  # Unpack the tuple, ignore reasoning
        # print(f"Territory: {territory}, Num troops: {num_troops}")
        if territory is None or num_troops is None:
            print(f"Error: Territory or num_troops is None")
            player.return_formatting_errors += 1
            return False
        if not self.game_state.check_terr_control(player.name, territory):
            print(f"Error: {player.name} does not control territory {territory}")
            player.troop_placement_errors += 1
            return False
        if num_troops > player.troops:
            print(f'''
                  Error: Not enough troops to place. {player.name} has only 
                  {player.troops} troop(s) left.'''
            )
            player.troop_placement_errors += 1
            return False
        return True

    def update_current_player_index(self):
        self.current_player_index = (
            (self.current_player_index + 1) % len(self.active_players)
        )
    
    def distribute_territories_random(self) -> int:
        if not self.game_state:
            raise ValueError("Game state is not initialized")
        self.current_player_index = (
            self.game_state.assign_territories_to_players_random(self.active_players))
        return self.current_player_index
    
    def choose_capitals(self) -> None:
        if self.rules.capitals: 
            for player in self.active_players:
                while player.capital is None:
                    capital = player.choose_capital(self.game_state)
                    player.capital = capital
                    self.game_state.set_capital(player.name, capital)

    @track_turn_time
    def intial_troop_placement_player(self, player: 'PlayerAgent') -> None:
        print(f"*****-------------NOW PLACING TROOPS FOR: -------------*****")
        print(f"Current player name: {player.name}")
        if player.troops > 0:
            player.set_interaction_context(
                game_round=self.game_round,
                turn_number=None,
                scope="initial_setup",
            )
            self.ensure_valid_move(player)

    def move_to_next_player(self):
        self.current_player_index = (
            (self.current_player_index + 1) % len(self.active_players)
        )
  
    def complete_initial_troop_placement(self):
        while any(player.troops > 0 for player in self.active_players):
            current_player = self.active_players[self.current_player_index]
            self.intial_troop_placement_player(current_player)
            self.move_to_next_player()

        corrrect_initial_troops =self.calculate_initial_troops(
            len(self.active_players))
        print(f"according to the rules, each player should have a total of "+
                  f" {corrrect_initial_troops} troops")
        for player in self.active_players:
            placed_troops = (
                    self.game_state.get_sum_of_player_troops(player.name))
            print(f"{player.name} has {placed_troops} troops")

        if all(self.game_state.get_sum_of_player_troops(player.name) == 
               corrrect_initial_troops for player in self.active_players):
            print("Initial troop placement complete")
        else:
            raise ValueError("Invalid territory assignment")

    def force_trade_in_cards(self, player: 'PlayerAgent') -> None:
        player_cards = self.player_cards.get(player.name)
        valid_combinations = self.rules.find_valid_combinations(
            player_cards,player.name, self.game_state)
        # Make the player propose a trade
        cards_to_trade, reasoning = player.must_trade_cards(player_cards,
            self.game_state, valid_combinations)

        event = self._build_turn_event(
            player,
            "mandatory_card_trade",
            1,
            reasoning,
            valid=False,
            error=None,
            selected_cards=cards_to_trade,
            cards_in_hand_before=len(player_cards),
            troops_awarded=0,
        )
        
        if cards_to_trade is None:
            print(f"{player.name} failed to provide valid response to cards.")
            player.return_formatting_errors += 1
            event["error"] = f"{player.name} failed to provide valid response to cards."
            event["outcome"] = "invalid"
            self._record_turn_event(event)
            return
        else:
            print(cards_to_trade)
            cards_to_trade
            selected_cards = [player_cards[i - 1] for i in cards_to_trade]
            # Verify the proposed trade using the rules instance
            print(selected_cards)
        
            valid, troops, _ = self.rules.verify_card_combination(
                selected_cards, player.name, self.game_state)

            if valid:
                # Remove the traded cards from the player's hand
                for card in selected_cards:
                    player_cards.remove(card)
                    self.discarded_cards.append(card)

                # Grant the player the corresponding troops
                player.troops += troops
                self.rules.trade_count += 1
                print(f"{player.name} traded in cards for {troops} extra troops.")
                event["valid"] = True
                event["outcome"] = "trade_completed"
                event["troops_awarded"] = troops
                event["cards_in_hand_after"] = len(player_cards)
            else:
                player.card_trade_errors += 1
                print(f"Invalid trade attempt by {player.name}.")
                event["error"] = f"Invalid trade attempt by {player.name}."
                event["outcome"] = "invalid"
                event["cards_in_hand_after"] = len(player_cards)

            self._record_turn_event(event)

    def ask_to_trade_in_cards(self, player: 'PlayerAgent') -> None:
        player_cards = self.player_cards.get(player.name)
        # Ask the player if they want to trade in cards
        valid_combinations = self.rules.find_valid_combinations(
            player_cards, player.name, self.game_state)
        cards_to_trade, reasoning = player.may_trade_cards(player_cards, 
            self.game_state, valid_combinations)

        event = self._build_turn_event(
            player,
            "optional_card_trade",
            1,
            reasoning,
            valid=False,
            error=None,
            selected_cards=cards_to_trade,
            cards_in_hand_before=len(player_cards),
            troops_awarded=0,
        )
        
        if cards_to_trade is None:
            print(f"{player.name} failed to provide valid response to cards.")
            player.return_formatting_errors += 1
            event["error"] = f"{player.name} failed to provide valid response to cards."
            event["outcome"] = "invalid"
            self._record_turn_event(event)
            return

        if cards_to_trade == [0]:
            print(f"{player.name} chose not to trade in cards.")
            event["valid"] = True
            event["outcome"] = "declined"
            event["cards_in_hand_after"] = len(player_cards)
            self._record_turn_event(event)
            return
        else:
            print(cards_to_trade)
            selected_cards = [player_cards[i - 1] for i in cards_to_trade]
            # Verify the proposed trade using the rules instance
            valid, troops, _ = self.rules.verify_card_combination(
                selected_cards,player.name, self.game_state)

            if valid:
                # Remove the traded cards from the player's hand
                for card in selected_cards:
                    player_cards.remove(card)
                    self.discarded_cards.append(card)

                # Grant the player the corresponding troops
                player.troops += troops
                self.rules.trade_count += 1
                print(f"{player.name} traded in cards for {troops} extra troops.")
                event["valid"] = True
                event["outcome"] = "trade_completed"
                event["troops_awarded"] = troops
                event["cards_in_hand_after"] = len(player_cards)
            else:
                player.card_trade_errors += 1
                print(f"Invalid trade attempt by {player.name}.")
                event["error"] = f"Invalid trade attempt by {player.name}."
                event["outcome"] = "invalid"
                event["cards_in_hand_after"] = len(player_cards)

            self._record_turn_event(event)

  
        # end phase 0

    def phase_1_troop_placement(self, player: 'PlayerAgent')-> None:
        self.phase = 1
        player.troops = 0

        # figure out if the player needs to trade in cards (i.e. has 5 or more cards)
        while len(self.player_cards[player.name]) >= 5:
            self.force_trade_in_cards(player)
        
        if (len(self.player_cards[player.name]) >= 3):
            # check if the player has a set of cards that can be traded in
            if self.rules.has_valid_combination(self.player_cards[player.name]):
                 self.ask_to_trade_in_cards(player)

        # figure out how many troops the player gets
        total_troops_from_territories = self.rules.calculate_troops(
            self.game_state.get_player_territories(player.name),self.game_state)
        
        player.troops += total_troops_from_territories
        # ensure the player places all their troops on the board
        self.ensure_valid_move(player)

        # end phase 1

    def phase_2_attack(self, player: 'PlayerAgent') -> int:
        self.phase = 2
        # print(f"{player.name} is attacking")
    
        successful_attacks, game_over = self.ensure_valid_attack_move(player)

        # if game is over, return to end the game
        if self.game_over:
            return successful_attacks
       

        if successful_attacks > 0:  # Player gets a card if they won an attack
            card = self.deck.draw_card(self.discarded_cards)
            self.player_cards[player.name].append(card)
            print(
                f"{player.name} conquered at least one territory this turn "
                f"and received a card"
            )
        return successful_attacks


    def phase_3_fortify(self, player: 'PlayerAgent') -> None:
        self.phase = 3
        print(f"{player.name} is fortifying")
        self.ensure_valid_fortify_move(player)

    # def is_game_over(self) -> bool:
    #     if self.rules.capitals:
    #         # Check if any player controls all capitals
    #         for player in self.active_players:
    #             player_territories = (
    #                 self.game_state.get_player_territories(player.name))
    #             if all(capital in player_territories for 
    #                    capital in self.game_state.capitals.values()):
    #                 return True  # This player controls all capitals, game over
    #     else:
    #         # Check if any player controls all territories
    #         for player in self.active_players:
    #             player_territories = (
    #                 self.game_state.get_player_territories(player.name))
    #             if len(player_territories) == len(self.game_state.territories_df):
    #                 return True  # This player controls all territories, game over

    #     return False  # No victory condition met, game continues
    

    def is_game_over(self) -> bool:
        print("Checking victory conditions")
        for player in self.active_players:
            game_over, winner_name, victory_condition = (
                self.rules.check_victory_conditions(
                    self.game_state, player, self.game_round, 
                    self.active_players))
            if game_over:
                self.game_over = True
                self.winner = next(p for p in self.players if p.name == winner_name) if winner_name else None
                self.victory_condition = victory_condition
                return True
        return False

    def validate_move_phase_1(
        self, player: 'PlayerAgent', 
        moves: List[Dict[str, int]], 
        reasoning: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        total_troops = 0

        for move in moves:
            territory = move.get('territory_name')
            num_troops = move.get('num_troops')
            
            #print(f'''Validating move: Territory: {territory}, 
            #      Num troops: {num_troops}''')

            if territory is None or num_troops is None:
                error_msg = f"Error: Territory or num_troops is None"
                player.return_formatting_errors += 1
                print(error_msg)
                return False, error_msg

            if not self.game_state.check_terr_control(player.name, territory):
                error_msg = (f"Error: {player.name} does not control territory " +
                            f"{territory}")
                player.troop_placement_errors += 1
                print(error_msg)
                return False, error_msg

            total_troops += num_troops

        if total_troops > player.troops:
            error_msg = (
            f"Error: Not enough troops to place. {player.name} has only " + 
            f"{player.troops} troop(s) left but trying to place {total_troops}.")
            print(error_msg)
            player.troop_placement_errors += 1
            return False, error_msg

        if total_troops < player.troops:
            error_msg = (
            f"Error: Not placing all troops. {player.name} is trying to place " +
            f"{total_troops} troop(s) but has {player.troops}.")
            print(error_msg)
            player.troop_placement_errors += 1
            return False, error_msg

        # Optionally handle reasoning here
        if reasoning:
            # print(f"Reasoning: {reasoning}")
            pass

        return True, None  # All moves are valid
    
    def validate_move_phase_0(
        self, player: 'PlayerAgent', 
        moves: List[Dict[str, int]], 
        reasoning: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:

        territory = moves[0].get('territory_name')
        num_troops = moves[0].get('num_troops')
   
        if territory is None or num_troops is None:
            error_msg = f"Error: Territory or num_troops is None"
            player.return_formatting_errors += 1
            print(error_msg)
            return False, error_msg

        if not self.game_state.check_terr_control(player.name, territory):
            error_msg = (f"Error: {player.name} does not control territory " +
                        f"{territory}")
            player.troop_placement_errors += 1
            print(error_msg)
            return False, error_msg

        if num_troops != 1:
            error_msg = (f"Error: Invalid number of troops to place. " +
                        f"Expected 1 troop but got {num_troops}")
            player.troop_placement_errors += 1
            print(error_msg)
            return False, error_msg
        
        # Optionally handle reasoning here
        if reasoning:
            # print(f"Reasoning: {reasoning}")
            pass

        return True, None  # All moves are valid

    def ensure_valid_move(
        self, player: 'PlayerAgent')-> None:
        valid_move = False
        invalid_moves = 0
        error_msg = None
        phase_name = (
            "initial_troop_placement" if self.phase == 0 else "troop_placement"
        )

        while not valid_move:
            if self.phase == 1 and player.turn_time_exhausted:
                print("Turn timer expired during placement, applying random fallback.")
                moves = self.generate_random_troop_placement(
                    player,
                    self.game_state,
                    initial_placement=False,
                )
                reasoning = "Turn timer expired; random troop placement"
                is_valid, error_msg = self.validate_move_phase_1(
                    player, moves, reasoning
                )

                pre_state = snapshot_player_state(self.game_state, player.name)
                fallback_event = {
                    "phase": phase_name,
                    "attempt": invalid_moves + 1,
                    "valid": is_valid,
                    "error": error_msg,
                    "reasoning": reasoning,
                    "raw_response": None,
                    "fallback": True,
                    "moves": [dict(move) for move in moves],
                    "pre_state": pre_state,
                }

                if is_valid:
                    self.update_game_state_for_multiple_moves(player, moves)
                    self.reduce_player_troops_for_multiple_moves(player, moves)
                    fallback_event["outcome"] = "applied"
                    fallback_event["post_state"] = snapshot_player_state(
                        self.game_state, player.name
                    )
                    self._record_turn_event(fallback_event)
                    return

                fallback_event["outcome"] = "invalid"
                fallback_event["post_state"] = pre_state
                self._record_turn_event(fallback_event)
                raise ValueError("Random troop placement failed after timer expiry")

            if self.phase == 0:
                # Phase 0: Initial troop placement 
                # (single move treated as a list with one move)
                moves, reasoning, _  = (
                    player.make_initial_troop_placement(
                        self.rules, self.game_state, error_msg))
                
                is_valid, error_msg = self.validate_move_phase_0(
                    player, moves, reasoning)

            elif self.phase == 1:
                # Phase 1: Troop placement (multiple moves)
                moves, reasoning, _ = (
                    player.make_troop_placement(
                        self.rules, self.game_state, error_msg))
                # Validate the moves
                is_valid, error_msg = self.validate_move_phase_1(
                    player, moves, reasoning)
            
            else:
                raise ValueError(f"Unknown phase: {self.phase}")

            pre_state = snapshot_player_state(self.game_state, player.name)
            event = self._build_turn_event(
                player,
                phase_name,
                invalid_moves + 1,
                reasoning,
                is_valid,
                error_msg,
                moves=[dict(move) for move in moves],
                pre_state=pre_state,
            )
            
            if is_valid:
                # print("Moves are valid")
                self.update_game_state_for_multiple_moves(player, moves)
                self.reduce_player_troops_for_multiple_moves(player, moves)
                event["outcome"] = "applied"
                event["post_state"] = snapshot_player_state(
                    self.game_state, player.name
                )
                self._record_turn_event(event)
                valid_move = True
            elif invalid_moves >= 3:
                event["outcome"] = "invalid"
                event["post_state"] = pre_state
                self._record_turn_event(event)
                print("Too many invalid moves, random troop placement turn")
                if self.phase == 0:
                    intial_placement = True
                else:
                    intial_placement = False
                moves = self.generate_random_troop_placement(
                    player, self.game_state, initial_placement=intial_placement) 
                reasoning = "Random troop placement"

                if self.phase == 0:
                    is_valid, error_msg = self.validate_move_phase_0(
                        player, moves, reasoning)
                else:
                    is_valid, error_msg = self.validate_move_phase_1(
                        player, moves, reasoning)

                fallback_pre_state = snapshot_player_state(self.game_state, player.name)
                fallback_event = {
                    "phase": phase_name,
                    "attempt": invalid_moves + 2,
                    "valid": is_valid,
                    "error": error_msg,
                    "reasoning": reasoning,
                    "raw_response": None,
                    "fallback": True,
                    "moves": [dict(move) for move in moves],
                    "pre_state": fallback_pre_state,
                }

                if is_valid:
                    # print("Random moves are valid")
                    self.update_game_state_for_multiple_moves(player, moves)
                    self.reduce_player_troops_for_multiple_moves(player, moves)
                    fallback_event["outcome"] = "applied"
                    fallback_event["post_state"] = snapshot_player_state(
                        self.game_state, player.name
                    )
                    self._record_turn_event(fallback_event)
                    valid_move = True
                else:
                    fallback_event["outcome"] = "invalid"
                    fallback_event["post_state"] = fallback_pre_state
                    self._record_turn_event(fallback_event)
                    raise ValueError("Random troop placement failed")
                
            else:
                event["outcome"] = "invalid"
                event["post_state"] = pre_state
                self._record_turn_event(event)
                print(f"Moves are invalid: {error_msg}, asking for new moves")
                invalid_moves += 1

    def ensure_valid_fortify_move(
        self, player: 'PlayerAgent')-> None:
        fortify_tries = 0
        error_msg = None

        while fortify_tries < 3:
            moves, reasoning, from_territory = (
                player.make_fortify_move(self.rules,
                    self.game_state, error_msg)
            ) 
            # print(f"Proposed moves: {moves}, Reasoning: {reasoning}")
            is_valid, error_msg = self.validate_fortify_move(
                player, moves, reasoning, from_territory)

            pre_state = snapshot_player_state(self.game_state, player.name)
            move = moves[0]
            event = self._build_turn_event(
                player,
                "fortify",
                fortify_tries + 1,
                reasoning,
                is_valid,
                error_msg,
                from_territory=from_territory,
                to_territory=move.get("territory_name"),
                moved_troops=move.get("num_troops"),
                moves=[dict(move)],
                pre_state=pre_state,
            )

            if is_valid:
                # print("Moves are valid")
                self.update_game_state_for_fortify_move(
                    player, moves, from_territory)
                if move.get("territory_name") == "Blank" or move.get("num_troops") == 0:
                    event["outcome"] = "skip"
                else:
                    event["outcome"] = "applied"
                event["post_state"] = snapshot_player_state(
                    self.game_state, player.name
                )
                self._record_turn_event(event)
                fortify_tries = 4  # Exit the loop
            else:
                event["outcome"] = "invalid"
                event["post_state"] = pre_state
                self._record_turn_event(event)
                print(f"Moves are invalid,\n{error_msg}\n Asking for new moves")
                fortify_tries += 1
    
    def validate_fortify_move(
        self, player: 'PlayerAgent', 
        moves: List[Dict[str, int]], 
        reasoning: Optional[str] = None,
        from_territory: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
       
        territory = moves[0].get('territory_name')
        num_troops = moves[0].get('num_troops')

        if territory is None or num_troops is None:
            error_msg = f"Error: Territory or num_troops is None"
            print(error_msg)
            player.return_formatting_errors += 1
            return False, error_msg
        
        if territory == 'Blank' or num_troops == 0:
            print("Choosing to not fortify")
            return True, None  # Blank move is valid

        if not self.game_state.check_terr_control(
            player.name, territory):
            error_msg = (f"Error: {player.name} does not control to " +
                    f"territory {territory}")
            print(error_msg)
            player.fortify_errors += 1
            return False ,error_msg
            
        if not self.game_state.check_terr_control(
            player.name, from_territory):
            error_msg = (f"Error: {player.name} does not control from " +
                    f"territory {territory}")
            print(error_msg)
            player.fortify_errors += 1
            return False ,error_msg
        
        from_territory_troops = self.game_state.check_number_of_troops(
            player.name, from_territory) 

        if num_troops >= from_territory_troops:
            error_msg = (f"Error: Not enough troops to fortify. {player.name} " +
            f"has only {from_territory_troops} troop(s) in {from_territory} " +
            f"but trying to move {num_troops}.")
            print(error_msg)
            player.fortify_errors += 1
            return False ,error_msg
        
        # Check if the territories are connected
        if not self.game_state.are_territories_connected(
            player.name, from_territory, territory):
            error_msg = f"Error: Territories are not connected"
            print(error_msg)
            player.fortify_errors += 1
            return False ,error_msg

        # Optionally handle reasoning here
        if reasoning:
            # print(f"Reasoning: {reasoning}")
            pass

        return True, None  # All moves are valid
    
    def update_game_state_for_fortify_move(
        self, player: 'PlayerAgent', moves: List[Dict[str, int]],
        from_territory: str)-> None:
        for move in moves:
            territory = move['territory_name']
            num_troops = move['num_troops']
            if territory == 'Blank' or num_troops == 0:
                return
            # update troops for the to_territory
            self.game_state.update_troops(player.name, territory, num_troops)
            #update the troops for the from_territory
            self.game_state.update_troops(player.name, from_territory, -num_troops)

    def update_game_state_for_multiple_moves(
            self, player: 'PlayerAgent', moves: List[Dict[str, int]])-> None:
        # Iterate over each move and apply it to the game state
        for move in moves:
            territory = move['territory_name']
            num_troops = move['num_troops']
            # Update the game state (for example, add troops to the territory)
            self.game_state.update_troops(player.name, territory, num_troops)

    def reduce_player_troops_for_multiple_moves(
            self, player: 'PlayerAgent', moves: List[Dict[str, int]])-> None:
        # Reduce the player's troop count based on the total troops placed
        total_troops = sum(move['num_troops'] for move in moves)
        player.troops -= total_troops

    def ensure_valid_attack_move(
        self, player: 'PlayerAgent')-> Tuple[int, Optional[bool]]:
        invalid_attacks = 0
        lost_attacks = 0
        successful_attacks = 0
        error_msg = None

        while invalid_attacks < 3:
            move, reasoning, from_territory = (
                player.make_attack_move(self.rules,
                    self.game_state, successful_attacks, 
                                        error_msg)
            ) 
            # print(f"Proposed attack: {move} from {from_territory}, " +
            #       f"Reasoning: {reasoning}")
            
            is_valid, error_msg = self.validate_attack_move(
                player, move, reasoning, from_territory)

            pre_state = snapshot_player_state(self.game_state, player.name)
            proposed_move = move[0]
            event = self._build_turn_event(
                player,
                "attack",
                invalid_attacks + 1,
                reasoning,
                is_valid,
                error_msg,
                from_territory=from_territory,
                target_territory=proposed_move.get("territory_name"),
                attack_troops=proposed_move.get("num_troops"),
                successful_attacks_so_far=successful_attacks,
                moves=[dict(proposed_move)],
                pre_state=pre_state,
            )

            if is_valid:
                self._print_attack_console_line(
                    player,
                    from_territory,
                    proposed_move.get("territory_name"),
                    proposed_move.get("num_troops"),
                )
                # print("Moves are valid")
                # calculate the outcome of the attack
                outcome, defender = (
                    self.game_state.update_game_state_for_attack_move(
                    player, move, from_territory))
                defender_eliminated = False
                if outcome == 'no_attack':
                    print("No attack was made")
                    event["outcome"] = "no_attack"
                    event["defender"] = None
                    event["post_state"] = pre_state
                    self._record_turn_event(event)
                    invalid_attacks = 4  # Exit the loop
                elif outcome == 'win':
                    successful_attacks += 1
                    # print("Player won the attack")
                    if not self.game_state.has_remaining_territories(defender):
                        print(f"{defender} has been eliminated!")
                        defender_eliminated = True
                        # Transfer cards from the eliminated player to the attacker
                        if defender in self.player_cards:
                            (self.player_cards[player.name].extend(
                                self.player_cards[defender]))
                            del self.player_cards[defender]

                            # remove the eliminated player from the active players list
                            self.remove_player(defender)
                    event["outcome"] = "win"
                    event["defender"] = defender
                    event["defender_eliminated"] = defender_eliminated
                    event["post_state"] = snapshot_player_state(
                        self.game_state, player.name
                    )
                    self._print_attack_outcome_console_line(
                        player=player,
                        defender_name=defender,
                        target_territory=proposed_move.get("territory_name"),
                        outcome=outcome,
                    )
                    self._record_turn_event(event)
                    # check if victory condition is met
                    if self.is_game_over():
                        self.game_over = True
                        return successful_attacks, self.game_over
                    
                    # Check if the attacker needs to trade cards
                    if len(self.player_cards[player.name]) > 5:
                        print(f"{player.name} has more than 5 cards. " +
                              f"Forcing card trade...")
                        self.force_trade_in_cards(player)


                else:
                    # print("Player lost the attack")
                    lost_attacks += 1
                    event["outcome"] = "lose"
                    event["defender"] = defender
                    event["post_state"] = snapshot_player_state(
                        self.game_state, player.name
                    )
                    self._print_attack_outcome_console_line(
                        player=player,
                        defender_name=defender,
                        target_territory=proposed_move.get("territory_name"),
                        outcome=outcome,
                    )
                    self._record_turn_event(event)
                
            else:
                invalid_attacks += 1
                event["outcome"] = "invalid"
                event["post_state"] = pre_state
                self._record_turn_event(event)
                print(f"Moves are invalid:\n{error_msg}\nAsking for new moves")
        return successful_attacks, self.game_over

    def validate_attack_move(
        self, player: 'PlayerAgent', 
        move: List[Dict[str, int]], 
        reasoning: Optional[str] = None,
        from_territory: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:    
        total_troops = 0
       
        territory = move[0].get('territory_name')
        num_troops = move[0].get('num_troops')
        
        #print(f'''Validating move: Territory: {territory}, 
        #        Num troops: {num_troops}''')

        if territory is None or num_troops is None:
            error_msg = f"Error: Territory or num_troops is None"
            print(error_msg)
            player.return_formatting_errors
            return False, error_msg
        
        if territory == 'Blank' or num_troops == 0:
            print("Choosing to not attack!!")
            return True, None  # Blank move is valid

        if self.game_state.check_terr_control(
            player.name, territory):
            error_msg = (f"Error: {player.name} already controls " +
                  f"territory {territory}")
            print(error_msg)
            player.attack_errors += 1
            return False, error_msg
            
        if not self.game_state.check_terr_control(
            player.name, from_territory):
            error_msg = (f"Error: {player.name} does not control from " +
                f"territory {territory}")
            print(error_msg)
            player.attack_errors += 1
            return False, error_msg
        
        from_territory_troops = self.game_state.check_number_of_troops(
            player.name, from_territory) 

        if num_troops >= from_territory_troops:
            error_msg = (f"Error: Not enough troops to Attack. {player.name} " +
            f"has only {from_territory_troops} troop(s) in {from_territory} " +
            f"but trying to attack with {num_troops}.")
            print(error_msg)
            player.attack_errors += 1
            return False, error_msg
        
        # Check if the territories are adjacent
        if not self.game_state.check_if_adjacent(from_territory, territory):
            error_msg = f"Error: Territories are not connected"
            print(error_msg)
            player.attack_errors += 1
            return False, error_msg

        # Optionally handle reasoning here
        if reasoning:
            # print(f"Reasoning: {reasoning}")
            pass

        return True, None  # All moves are valid

    def generate_random_troop_placement(self, player: 'PlayerAgent', 
        game_state: 'GameState'
    ) -> List[Dict[str, int]]:
        """
        Generates a random troop placement for a player. The function will randomly
        distribute the player's available troops across the territories they control.

        Parameters:
        - player: The player for whom to generate the move.
        - game_state: The current state of the game.

        Returns:
        - A list of dictionaries representing the troop placement move. 
        Each dictionary contains a territory name and the number of troops placed there.
        """

        # Get the list of territories the player controls
        controlled_territories = game_state.get_player_territories(player.name)

        # Total troops to allocate
        troops_to_allocate = player.troops

        # Initialize an empty list to store the troop placement moves
        troop_placement = []

        # Randomly distribute troops among controlled territories
        for territory in controlled_territories:
            if troops_to_allocate <= 0:
                break

            # Randomly decide the number of troops to place in the current territory
            troops_for_this_territory = random.randint(1, troops_to_allocate)
            troop_placement.append({'territory_name': territory, 'num_troops': troops_for_this_territory})

            # Subtract the allocated troops from the total remaining troops
            troops_to_allocate -= troops_for_this_territory

        # If there are still troops remaining, distribute them across the territories randomly
        while troops_to_allocate > 0:
            for move in troop_placement:
                if troops_to_allocate <= 0:
                    break
                move['num_troops'] += 1
                troops_to_allocate -= 1

        return troop_placement
    

    def generate_random_troop_placement(
        self, 
        player: 'PlayerAgent', 
        game_state: 'GameState', 
        initial_placement: bool = False
    ) -> List[Dict[str, int]]:
        """
        Generates a random troop placement for a player. The function will randomly
        distribute the player's available troops across the territories they control.
        
        If `initial_placement` is True, the player only allocates 1 troop.

        Parameters:
        - player: The player for whom to generate the move.
        - game_state: The current state of the game.
        - initial_placement: A flag indicating whether this is the initial troop placement.
        
        Returns:
        - A list of dictionaries representing the troop placement move. 
        Each dictionary contains a territory name and the number of troops placed there.
        """

        # Get the list of territories the player controls
        controlled_territories = game_state.get_player_territories(player.name)

        # Total troops to allocate
        troops_to_allocate = 1 if initial_placement else player.troops

        # Initialize an empty list to store the troop placement moves
        troop_placement = []

        # Randomly distribute troops among controlled territories
        for territory in controlled_territories:
            if troops_to_allocate <= 0:
                break

            # For initial placement, only allocate 1 troop
            if initial_placement:
                troop_placement.append({'territory_name': territory, 'num_troops': 1})
                break  # Only place one troop
            else:
                # Randomly decide the number of troops to place in the current territory
                troops_for_this_territory = random.randint(1, troops_to_allocate)
                troop_placement.append({'territory_name': territory, 'num_troops': troops_for_this_territory})

                # Subtract the allocated troops from the total remaining troops
                troops_to_allocate -= troops_for_this_territory

        # If there are still troops remaining and it's not the initial placement, distribute them
        if not initial_placement:
            while troops_to_allocate > 0:
                for move in troop_placement:
                    if troops_to_allocate <= 0:
                        break
                    move['num_troops'] += 1
                    troops_to_allocate -= 1

        return troop_placement

        
    @track_turn_time
    def play_a_turn(
        self, player: 'PlayerAgent', turn_number: Optional[int] = None
    ) -> Dict[str, Any]:
        print(f"---------Player {player.name} is starting their turn.----------")
        player.set_interaction_context(
            game_round=self.game_round,
            turn_number=turn_number,
            scope="turn",
        )
        self._start_turn_trace(player)
        planning_started_at = time.time()
        player.define_strategy_for_move(self.rules, self.game_state)
        planning_elapsed = time.time() - planning_started_at
        self._capture_turn_plan(player)
        self._print_phase_completion(
            player=player,
            completed_phase="planning mode",
            elapsed_seconds=planning_elapsed,
            next_phase=(
                f"execution turn timer ({player.turn_time_limit_seconds}s) "
                "and placement mode"
            ),
            planning=True,
            include_plan=True,
        )
        player.start_turn_timer(player.turn_time_limit_seconds)
        # Phase 1: Troop Placement
        placement_started_at = time.time()
        self.phase_1_troop_placement(player)
        placement_elapsed = time.time() - placement_started_at
        if not player.turn_time_exhausted:
            self._print_phase_completion(
                player=player,
                completed_phase="placement mode",
                elapsed_seconds=placement_elapsed,
                next_phase="attack mode",
            )
        if not player.turn_time_exhausted:
            attack_started_at = time.time()
            successful_attacks = self.phase_2_attack(player)
            attack_elapsed = time.time() - attack_started_at
            next_phase = None
            if not self.game_over and not player.turn_time_exhausted:
                next_phase = "fortify mode"
            self._print_phase_completion(
                player=player,
                completed_phase="attack mode",
                elapsed_seconds=attack_elapsed,
                next_phase=next_phase,
                extra_detail=f"successful attacks {successful_attacks}",
            )
        else:
            print(f"{player.name} exhausted the turn timer during placement.")
        if not self.game_over and not player.turn_time_exhausted:
            fortify_started_at = time.time()
            self.phase_3_fortify(player)
            fortify_elapsed = time.time() - fortify_started_at
            self._print_phase_completion(
                player=player,
                completed_phase="fortify mode",
                elapsed_seconds=fortify_elapsed,
            )
        print(f"{player.name} has completed their turn.")
        completed_turn = self._finalize_turn_trace(player, turn_number)
        player.clear_turn_timer()
        return completed_turn
    
    def play_game(self, include_initial_troop_placement:bool = True,
                  base_folder: str | None = None
    ) -> str:
        if base_folder is None:
            base_folder = str(get_game_results_dir())
        
        turn_number = 0
        games_folder = create_game_folder(base_folder=base_folder)
        self.llm_interaction_logger = build_llm_interaction_logger(games_folder)

        self.init_game_state()
        save_game_manifest(
            self,
            games_folder,
            include_initial_troop_placement=include_initial_troop_placement,
        )

        if include_initial_troop_placement:
            self.distribute_territories_random()
            self.choose_capitals()
            self.complete_initial_troop_placement()
        else:
            self.game_state.territories_df = pd.read_csv('territories.csv')


        # save the first snapshot of the game state
        save_game_state(self.game_state, games_folder, turn_number, 
                               self.game_round)
        save_player_data(self.players, games_folder, turn_number, 
                                self.game_round)

        while not self.is_game_over():
            print(f"this is the game_round var: {self.game_round}" )
            self.game_round += 1

            print(f'This is the current game state:----------')
            print(self.game_state.territories_df)
            for player in list(self.active_players):
                if player not in self.active_players:
                    continue
                # print(f"these are the active players_:{self.active_players}")
                # distribute some cards to test logic needs to be taken out
                # just used for testing card logic
                # if self.game_round == 1:
                #     for _ in range(5):
                #         card = self.deck.draw_card(self.discarded_cards)
                #         self.player_cards[player.name].append(card)
                
                turn_number += 1
                turn_summary = self.play_a_turn(player, turn_number)
                save_game_state(self.game_state, games_folder, turn_number, 
                               self.game_round)
                save_player_data(self.players, games_folder, turn_number, 
                                self.game_round)
                save_turn_summary(turn_summary, games_folder, turn_number)

                # check if the game is over
                if self.is_game_over():
                    break
 
        print(f"Game Over! The winner is {self.winner.name} by "+
              f"{self.victory_condition}")
        print(f"Game lasted {self.game_round} rounds")
        save_end_game_results(self.players, 
                          self.winner.name if self.winner else None, 
                          self.victory_condition, 
                          self.game_round, 
                          games_folder, self.game_state)
        return games_folder
