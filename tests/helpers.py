from risk_game.game_config import GameConfig
from risk_game.game_constants import TERRITORIES
from risk_game.game_master import GameMaster
from risk_game.game_state import GameState
from risk_game.llm_clients.llm_base import LLMClient
from risk_game.player_agent import PlayerAgent
from risk_game.rules import Rules


class StubLLMClient(LLMClient):
    def __init__(self) -> None:
        super().__init__(provider_name="stub", model_type="stub")

    def get_chat_completion(self, messages) -> str:
        return "stub-response"


class RecordingLLMClient(LLMClient):
    def __init__(self, response: str = "stub-response") -> None:
        super().__init__(provider_name="recording", model_type="recording")
        self.response = response
        self.last_message = None

    def get_chat_completion(self, messages) -> str:
        self.last_message = messages
        return self.response


class ScriptedAgent(PlayerAgent):
    def __init__(
        self,
        name: str,
        attack_margin: int = 0,
        attack_limit_per_turn: int = 2,
    ) -> None:
        super().__init__(name, StubLLMClient())
        self.attack_margin = attack_margin
        self.attack_limit_per_turn = attack_limit_per_turn
        self._turn_attack_count = 0

    def choose_capital(self, game_state: GameState) -> str:
        territories = game_state.get_player_territories(self.name)
        capital = max(
            territories,
            key=lambda territory: (
                len(game_state.territories_graph.get(territory, [])),
                territory,
            ),
        )
        self.capital = capital
        return capital

    def define_strategy_for_move(self, rules: Rules, game_state: GameState) -> None:
        self._turn_attack_count = 0
        self.turn_strategy = (
            "Concentrate on borders, attack favorable edges, fortify exposed fronts."
        )

    def make_initial_troop_placement(
        self, rules: Rules, game_state: GameState, error_msg: str | None = None
    ):
        territory = self._preferred_border_territory(game_state)
        return (
            [{"territory_name": territory, "num_troops": 1}],
            "Reinforce the most exposed border territory.",
            None,
        )

    def make_troop_placement(
        self, rules: Rules, game_state: GameState, error_msg: str | None = None
    ):
        territory = self._preferred_border_territory(game_state)
        return (
            [{"territory_name": territory, "num_troops": self.troops}],
            "Stack reinforcements on the best attack frontier.",
            None,
        )

    def make_attack_move(
        self,
        rules: Rules,
        game_state: GameState,
        successful_attacks: int,
        error_msg: str | None = None,
    ):
        if self._turn_attack_count >= self.attack_limit_per_turn:
            return (
                [{"territory_name": "Blank", "num_troops": 0}],
                "Attack limit reached for this turn.",
                "Blank",
            )

        candidates = self._attack_candidates(game_state)
        if not candidates:
            return (
                [{"territory_name": "Blank", "num_troops": 0}],
                "No favorable attacks available.",
                "Blank",
            )

        _, attack_troops, from_territory, target_territory = candidates[0]
        self._turn_attack_count += 1
        return (
            [{"territory_name": target_territory, "num_troops": attack_troops}],
            "Take the strongest favorable attack available.",
            from_territory,
        )

    def make_fortify_move(
        self, rules: Rules, game_state: GameState, error_msg: str | None = None
    ):
        border_territories = self._border_territories(game_state)
        if not border_territories:
            return (
                [{"territory_name": "Blank", "num_troops": 0}],
                "No border territory needs fortification.",
                "Blank",
            )

        target_territory = max(
            border_territories,
            key=lambda territory: (
                self._enemy_neighbor_count(game_state, territory),
                -game_state.check_number_of_troops(self.name, territory),
                territory,
            ),
        )

        movable_sources = []
        for territory, movable_troops in game_state.get_strong_territories_with_troops(
            self.name
        ):
            if territory == target_territory:
                continue
            if not game_state.are_territories_connected(
                self.name, territory, target_territory
            ):
                continue
            movable_sources.append((movable_troops, territory))

        if not movable_sources:
            return (
                [{"territory_name": "Blank", "num_troops": 0}],
                "No connected source territory available for fortification.",
                "Blank",
            )

        movable_troops, from_territory = max(movable_sources)
        transfer_troops = max(1, movable_troops // 2)

        return (
            [{"territory_name": target_territory, "num_troops": transfer_troops}],
            "Move troops from the strongest connected interior territory.",
            from_territory,
        )

    def must_trade_cards(
        self,
        cards,
        game_state: GameState,
        valid_combinations,
    ):
        return self._best_trade(valid_combinations), "Trade the highest value set."

    def may_trade_cards(
        self,
        cards,
        game_state: GameState,
        valid_combinations,
    ):
        best_trade = self._best_trade(valid_combinations)
        if best_trade is None:
            return [0], "No valid trade available."
        return best_trade, "Trade the highest value set."

    def _owned_territories(self, game_state: GameState) -> list[str]:
        return sorted(game_state.get_player_territories(self.name))

    def _border_territories(self, game_state: GameState) -> list[str]:
        borders = []
        for territory in self._owned_territories(game_state):
            if self._enemy_neighbor_count(game_state, territory) > 0:
                borders.append(territory)
        return borders

    def _enemy_neighbor_count(self, game_state: GameState, territory: str) -> int:
        return sum(
            1
            for neighbor in game_state.territories_graph.get(territory, [])
            if not game_state.check_terr_control(self.name, neighbor)
        )

    def _preferred_border_territory(self, game_state: GameState) -> str:
        border_territories = self._border_territories(game_state)
        candidate_territories = border_territories or self._owned_territories(game_state)
        return max(
            candidate_territories,
            key=lambda territory: (
                self._enemy_neighbor_count(game_state, territory),
                len(game_state.territories_graph.get(territory, [])),
                territory,
            ),
        )

    def _attack_candidates(
        self, game_state: GameState
    ) -> list[tuple[int, int, str, str]]:
        candidates = []
        for from_territory, movable_troops in game_state.get_strong_territories_with_troops(
            self.name
        ):
            if movable_troops <= 0:
                continue

            for target_territory in sorted(game_state.territories_graph[from_territory]):
                if game_state.check_terr_control(self.name, target_territory):
                    continue

                _, defender_troops = game_state.get_territory_control(target_territory)
                if movable_troops < defender_troops + self.attack_margin:
                    continue

                score = (
                    movable_troops - defender_troops,
                    -defender_troops,
                    self._enemy_neighbor_count(game_state, target_territory),
                )
                candidates.append(
                    (score, movable_troops, from_territory, target_territory)
                )

        candidates.sort(reverse=True)
        return candidates

    def _best_trade(self, valid_combinations):
        if not valid_combinations:
            return None

        best_value = max(valid_combinations)
        best_combinations = valid_combinations[best_value]
        best_indices, _ = min(best_combinations, key=lambda item: item[0])
        return best_indices


def make_rules(**config_overrides) -> Rules:
    config = GameConfig(**config_overrides)
    return Rules(config)


def make_players(*names: str):
    return [PlayerAgent(name, StubLLMClient()) for name in names]


def make_game_state(*names: str, **config_overrides):
    players = make_players(*names)
    rules = make_rules(**config_overrides)
    game_state = GameState(players, rules)
    return players, game_state, rules


def make_game_master(*names: str, **config_overrides) -> GameMaster:
    game_master = GameMaster(make_rules(**config_overrides))
    for name in names:
        game_master.add_player(name, StubLLMClient())
    game_master.init_game_state()
    return game_master


def make_scripted_game_master(*names: str, **config_overrides) -> GameMaster:
    game_master = GameMaster(make_rules(**config_overrides))
    game_master.players = [ScriptedAgent(name) for name in names]
    game_master.player_cards = {player.name: [] for player in game_master.players}
    return game_master


def get_player(players, name: str) -> PlayerAgent:
    return next(player for player in players if player.name == name)


def set_territory_owner(
    game_state: GameState, territory: str, player_name: str, troops: int
) -> None:
    row_mask = game_state.territories_df["Territory"] == territory
    player_columns = list(game_state.territories_df.columns[1:])
    game_state.territories_df.loc[row_mask, player_columns] = 0
    game_state.territories_df.loc[row_mask, player_name] = troops


def seed_full_board(game_state: GameState, player_names: list[str]) -> None:
    for index, territory in enumerate(TERRITORIES):
        player_name = player_names[index % len(player_names)]
        set_territory_owner(game_state, territory, player_name, 1)


def assert_valid_board_state(test_case, game_state: GameState) -> None:
    player_columns = list(game_state.territories_df.columns[1:])
    owner_counts = game_state.territories_df[player_columns].gt(0).sum(axis=1)

    test_case.assertEqual(len(game_state.territories_df), 42)
    test_case.assertTrue((owner_counts == 1).all())
    test_case.assertTrue((game_state.territories_df[player_columns] >= 0).all().all())


def owner_signature(game_state: GameState) -> tuple[tuple[str, str], ...]:
    signature = []
    for territory in TERRITORIES:
        owner, _ = game_state.get_territory_control(territory)
        signature.append((territory, owner))
    return tuple(signature)
