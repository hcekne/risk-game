from dataclasses import dataclass
from typing import List, Optional

import risk_game.game_master as gm
from risk_game.game_config import GameConfig
from risk_game.llm_clients import llm_client
from risk_game.rules import Rules


@dataclass(frozen=True)
class AgentSpec:
    name: str
    provider: str
    model: int | str
    reasoning_effort: Optional[str] = "none"
    use_responses_api: bool = True
    verbosity: str = "low"
    enable_thinking: bool = False
    thinking_budget: int = 2000
    thinking_effort: Optional[str] = None
    turn_time_limit_seconds: Optional[int] = None
    placement_time_limit_seconds: Optional[int] = None
    placement_reasoning_effort: Optional[str] = None
    planning_reasoning_effort: Optional[str] = None
    attack_reasoning_effort: Optional[str] = None
    fortify_reasoning_effort: Optional[str] = None
    card_trade_reasoning_effort: Optional[str] = None


def build_openai_gpt54_family(
    reasoning_effort: str = "none",
    verbosity: str = "low",
) -> List[AgentSpec]:
    return [
        AgentSpec(
            name="gpt-5.4",
            provider="OpenAI",
            model="gpt-5.4",
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
        ),
        AgentSpec(
            name="gpt-5.4-mini",
            provider="OpenAI",
            model="gpt-5.4-mini",
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
        ),
        AgentSpec(
            name="gpt-5.4-nano-a",
            provider="OpenAI",
            model="gpt-5.4-nano",
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
        ),
        AgentSpec(
            name="gpt-5.4-nano-b",
            provider="OpenAI",
            model="gpt-5.4-nano",
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
        ),
    ]


def build_openai_generation_ladder(
    verbosity: str = "low",
) -> List[AgentSpec]:
    return [
        AgentSpec(
            name="gpt-5.5",
            provider="OpenAI",
            model="gpt-5.5",
            reasoning_effort="medium",
            verbosity=verbosity,
        ),
        AgentSpec(
            name="gpt-5.4",
            provider="OpenAI",
            model="gpt-5.4",
            reasoning_effort="medium",
            verbosity=verbosity,
        ),
        AgentSpec(
            name="gpt-4.1",
            provider="OpenAI",
            model="gpt-4.1",
            reasoning_effort="none",
            verbosity=verbosity,
        ),
    ]


def build_openai_size_ladder(
    reasoning_effort: str = "medium",
    verbosity: str = "low",
) -> List[AgentSpec]:
    return [
        AgentSpec(
            name="gpt-5.4",
            provider="OpenAI",
            model="gpt-5.4",
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
        ),
        AgentSpec(
            name="gpt-5.4-mini",
            provider="OpenAI",
            model="gpt-5.4-mini",
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
        ),
        AgentSpec(
            name="gpt-5.4-nano",
            provider="OpenAI",
            model="gpt-5.4-nano",
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
        ),
    ]


def build_openai_nano_reasoning_arena(
    verbosity: str = "low",
) -> List[AgentSpec]:
    return [
        AgentSpec(
            name="gpt-5.4-nano-none",
            provider="OpenAI",
            model="gpt-5.4-nano",
            reasoning_effort="none",
            verbosity=verbosity,
        ),
        AgentSpec(
            name="gpt-5.4-nano-low",
            provider="OpenAI",
            model="gpt-5.4-nano",
            reasoning_effort="low",
            verbosity=verbosity,
        ),
        AgentSpec(
            name="gpt-5.4-nano-medium",
            provider="OpenAI",
            model="gpt-5.4-nano",
            reasoning_effort="medium",
            verbosity=verbosity,
        ),
        AgentSpec(
            name="gpt-5.4-nano-high",
            provider="OpenAI",
            model="gpt-5.4-nano",
            reasoning_effort="high",
            verbosity=verbosity,
        ),
    ]


def build_openai_mini_reasoning_arena(
    verbosity: str = "low",
) -> List[AgentSpec]:
    def _mini(reasoning_effort: str) -> AgentSpec:
        return AgentSpec(
            name=f"gpt-5.4-mini-{reasoning_effort}",
            provider="OpenAI",
            model="gpt-5.4-mini",
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
            placement_reasoning_effort=reasoning_effort,
            planning_reasoning_effort=reasoning_effort,
            attack_reasoning_effort=reasoning_effort,
            fortify_reasoning_effort=reasoning_effort,
            card_trade_reasoning_effort=reasoning_effort,
        )

    return [
        _mini("none"),
        _mini("low"),
        _mini("medium"),
        _mini("high"),
    ]


def build_openai_mini_medium_vs_high_arena(
    verbosity: str = "low",
) -> List[AgentSpec]:
    def _mini(name_suffix: str, reasoning_effort: str) -> AgentSpec:
        return AgentSpec(
            name=f"gpt-5.4-mini-{name_suffix}",
            provider="OpenAI",
            model="gpt-5.4-mini",
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
            placement_reasoning_effort=reasoning_effort,
            planning_reasoning_effort=reasoning_effort,
            attack_reasoning_effort=reasoning_effort,
            fortify_reasoning_effort=reasoning_effort,
            card_trade_reasoning_effort=reasoning_effort,
        )

    return [
        _mini("medium-a", "medium"),
        _mini("medium-b", "medium"),
        _mini("high-a", "high"),
        _mini("high-b", "high"),
    ]


def build_openai_mini_high_strategic_hybrid_arena(
    verbosity: str = "low",
) -> List[AgentSpec]:
    def _medium(name_suffix: str) -> AgentSpec:
        return AgentSpec(
            name=f"gpt-5.4-mini-medium-all-{name_suffix}",
            provider="OpenAI",
            model="gpt-5.4-mini",
            reasoning_effort="medium",
            verbosity=verbosity,
            placement_reasoning_effort="medium",
            planning_reasoning_effort="medium",
            attack_reasoning_effort="medium",
            fortify_reasoning_effort="medium",
            card_trade_reasoning_effort="medium",
        )

    def _hybrid(name_suffix: str) -> AgentSpec:
        return AgentSpec(
            name=f"gpt-5.4-mini-high-strategic-{name_suffix}",
            provider="OpenAI",
            model="gpt-5.4-mini",
            reasoning_effort="high",
            verbosity=verbosity,
            placement_reasoning_effort="medium",
            planning_reasoning_effort="high",
            attack_reasoning_effort="high",
            fortify_reasoning_effort="medium",
            card_trade_reasoning_effort="medium",
        )

    return [
        _medium("a"),
        _medium("b"),
        _hybrid("a"),
        _hybrid("b"),
    ]


def build_live_turn_frontier_roster(
    *,
    openai_model: str = "gpt-5.5",
    openai_reasoning_effort: str = "medium",
    openai_verbosity: str = "low",
    anthropic_model: str = "claude-opus-4-7",
    anthropic_enable_thinking: bool = False,
    anthropic_thinking_effort: Optional[str] = None,
    gemini_model: str = "gemini-3.1-pro-preview",
    gemini_reasoning_effort: str = "medium",
    moonshot_model: str = "kimi-k2.6",
    moonshot_enable_thinking: bool = False,
) -> List[AgentSpec]:
    """Build the experiment-ready cross-provider live-turn roster.

    These defaults are based on measured prompt-smoke and setting-probe runs:
    - OpenAI uses normal/medium reasoning by default.
    - Claude Opus 4.7 uses standard mode by default because it is faster than
      adaptive thinking while still clearing the live-turn prompt suite.
    - Gemini uses gemini-3.1-pro-preview as the chosen Google representative.
    - Kimi K2.6 runs with thinking disabled because thinking-enabled mode
      exceeded the synchronous placement and turn budgets.
    """

    return [
        AgentSpec(
            name=openai_model,
            provider="OpenAI",
            model=openai_model,
            reasoning_effort=openai_reasoning_effort,
            verbosity=openai_verbosity,
        ),
        AgentSpec(
            name=anthropic_model,
            provider="Anthropic",
            model=anthropic_model,
            enable_thinking=anthropic_enable_thinking,
            thinking_effort=anthropic_thinking_effort,
        ),
        AgentSpec(
            name=gemini_model,
            provider="Gemini",
            model=gemini_model,
            reasoning_effort=gemini_reasoning_effort,
        ),
        AgentSpec(
            name=moonshot_model,
            provider="Moonshot",
            model=moonshot_model,
            enable_thinking=moonshot_enable_thinking,
        ),
    ]


class Experiment:
    def __init__(
        self,
        config: GameConfig,
        agent_mix: int = 1,
        num_games: int = 10,
        agent_specs: Optional[List[AgentSpec]] = None,
    ) -> None:
        """
        Initialize the experiment with default options.

        Args:
        - config: The configuration for the game.
        - agent_mix: Preset integer mix to use when agent_specs is not supplied.
        - num_games: The number of games to run in the experiment.
        - agent_specs: Optional explicit player specs that override agent_mix.
        """
        self.config = config
        self.num_games = num_games
        self.agent_mix = agent_mix
        self.agent_specs = agent_specs or []

    def __repr__(self) -> str:
        if self.config.key_areas:
            key_areas = ", ".join(self.config.key_areas)
        else:
            key_areas = "None"

        return (
            f"Experiment Configuration:\n"
            f"Agent Mix: {self.agent_mix}\n"
            f"Explicit Agent Specs: {len(self.agent_specs)}\n"
            f"Number of Games: {self.num_games}\n"
            f"Progressive: {self.config.progressive}\n"
            f"Capitals: {self.config.capitals}\n"
            f"Territory Control Percentage: +"
            f"{self.config.territory_control_percentage:.2f}\n"
            f"Required Continents: {self.config.required_continents}\n"
            f"Key Areas: {key_areas}\n"
            f"Max Rounds: {self.config.max_rounds}\n"
            f"Turn Time Limit Seconds: {self.config.turn_time_limit_seconds}\n"
            f"Placement Time Limit Seconds: "
            f"{self.config.placement_time_limit_seconds}\n"
            f"Placement Reasoning Effort: "
            f"{self.config.placement_reasoning_effort}\n"
            f"Planning Reasoning Effort: "
            f"{self.config.planning_reasoning_effort}\n"
            f"Attack Reasoning Effort: "
            f"{self.config.attack_reasoning_effort}\n"
            f"Fortify Reasoning Effort: "
            f"{self.config.fortify_reasoning_effort}\n"
            f"Card Trade Reasoning Effort: "
            f"{self.config.card_trade_reasoning_effort}\n"
        )

    def _add_players_from_specs(
        self,
        game: gm.GameMaster,
        agent_specs: List[AgentSpec],
    ) -> None:
        for spec in agent_specs:
            runtime_overrides = {
                "turn_time_limit_seconds": spec.turn_time_limit_seconds,
                "placement_time_limit_seconds": spec.placement_time_limit_seconds,
                "placement_reasoning_effort": spec.placement_reasoning_effort,
                "planning_reasoning_effort": spec.planning_reasoning_effort,
                "attack_reasoning_effort": spec.attack_reasoning_effort,
                "fortify_reasoning_effort": spec.fortify_reasoning_effort,
                "card_trade_reasoning_effort": spec.card_trade_reasoning_effort,
            }
            game.add_player(
                name=spec.name,
                llm_client=llm_client.create_llm_client(
                    spec.provider,
                    spec.model,
                    use_responses_api=spec.use_responses_api,
                    reasoning_effort=spec.reasoning_effort,
                    verbosity=spec.verbosity,
                    enable_thinking=spec.enable_thinking,
                    thinking_budget=spec.thinking_budget,
                    thinking_effort=spec.thinking_effort,
                ),
                runtime_overrides=runtime_overrides,
            )

    def _preset_agent_specs(self) -> List[AgentSpec]:
        if self.agent_mix == 1:
            return build_openai_gpt54_family(reasoning_effort="none")
        if self.agent_mix == 2:
            return build_openai_nano_reasoning_arena()
        if self.agent_mix == 3:
            return build_openai_mini_reasoning_arena()
        if self.agent_mix == 4:
            return build_openai_mini_medium_vs_high_arena()

        return []

    def initialize_game(self) -> gm.GameMaster:
        """
        Initialize a single game with default rules and players.

        Returns:
        - game: An initialized GameMaster instance.
        """
        rules = Rules(self.config)
        game = gm.GameMaster(rules)

        if self.agent_specs:
            self._add_players_from_specs(game, self.agent_specs)
            return game

        preset_specs = self._preset_agent_specs()
        if preset_specs:
            self._add_players_from_specs(game, preset_specs)
            return game

        # Old agent mixes kept for reference/backward compatibility.
        if self.agent_mix == 10:
            game.add_player(
                name="llama3.1_70",
                llm_client=llm_client.create_llm_client("Groq", 1),
            )
            game.add_player(
                name="Claude_Sonnet_3_5",
                llm_client=llm_client.create_llm_client("Anthropic", 1),
            )
            game.add_player(
                name="gpt-5.4",
                llm_client=llm_client.create_llm_client(
                    "OpenAI",
                    "gpt-5.4",
                    reasoning_effort="none",
                ),
            )
        elif self.agent_mix == 11:
            game.add_player(
                name="Strong(gpt-5.4)",
                llm_client=llm_client.create_llm_client(
                    "OpenAI",
                    "gpt-5.4",
                    reasoning_effort="none",
                ),
            )
            game.add_player(
                name="Medium(gpt-5.4-mini)",
                llm_client=llm_client.create_llm_client(
                    "OpenAI",
                    "gpt-5.4-mini",
                    reasoning_effort="none",
                ),
            )
            game.add_player(
                name="Weak(gpt-5.4-nano)",
                llm_client=llm_client.create_llm_client(
                    "OpenAI",
                    "gpt-5.4-nano",
                    reasoning_effort="none",
                ),
            )
        elif self.agent_mix == 12:
            game.add_player(
                name="Big_llama3.1_400",
                llm_client=llm_client.create_llm_client("Bedrock", 1),
            )
            game.add_player(
                name="Claude_Sonnet_3_5",
                llm_client=llm_client.create_llm_client("Anthropic", 1),
            )
            game.add_player(
                name="gpt-5.4",
                llm_client=llm_client.create_llm_client(
                    "OpenAI",
                    "gpt-5.4",
                    reasoning_effort="none",
                ),
            )
        elif self.agent_mix == 13:
            game.add_player(
                name="Claude_Sonnet_3_5",
                llm_client=llm_client.create_llm_client("Anthropic", 1),
            )
            game.add_player(
                name="gpt-5.4",
                llm_client=llm_client.create_llm_client(
                    "OpenAI",
                    "gpt-5.4",
                    reasoning_effort="none",
                ),
            )
            game.add_player(
                name="Medium(gpt-5.4-mini)",
                llm_client=llm_client.create_llm_client(
                    "OpenAI",
                    "gpt-5.4-mini",
                    reasoning_effort="none",
                ),
            )
        else:
            raise ValueError(
                f"Unsupported agent_mix '{self.agent_mix}'. "
                "Use a known preset or pass explicit agent_specs."
            )

        return game

    def run_experiment(self) -> None:
        """Run the configured experiment."""
        for i in range(1, self.num_games + 1):
            print(f"Starting game {i}...")
            game = self.initialize_game()
            game.play_game(include_initial_troop_placement=True)
