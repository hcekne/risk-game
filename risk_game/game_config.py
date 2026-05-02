from typing import List, Dict, Any

class GameConfig:
    def __init__(self, 
                 progressive: bool = True, 
                 capitals: bool = False, 
                 territory_control_percentage: float = 0.65, 
                 required_continents: int = 0, 
                 key_areas: List[str] = None, 
                 max_rounds: int = 15,
                 turn_time_limit_seconds: int = 90,
                 planning_time_limit_seconds: int | None = None,
                 placement_time_limit_seconds: int = 15,
                 placement_reasoning_effort: str = "low",
                 planning_reasoning_effort: str = "medium",
                 attack_reasoning_effort: str = "medium",
                 fortify_reasoning_effort: str = "medium",
                 card_trade_reasoning_effort: str = "low") -> None:
        self.progressive = progressive
        self.capitals = capitals
        self.territory_control_percentage = territory_control_percentage
        self.required_continents = required_continents
        self.key_areas = key_areas or []
        self.max_rounds = max_rounds
        self.turn_time_limit_seconds = turn_time_limit_seconds
        self.planning_time_limit_seconds = planning_time_limit_seconds
        self.placement_time_limit_seconds = placement_time_limit_seconds
        self.placement_reasoning_effort = placement_reasoning_effort
        self.planning_reasoning_effort = planning_reasoning_effort
        self.attack_reasoning_effort = attack_reasoning_effort
        self.fortify_reasoning_effort = fortify_reasoning_effort
        self.card_trade_reasoning_effort = card_trade_reasoning_effort

    def to_dict(self) -> Dict[str, Any]:
        return {
            "progressive": self.progressive,
            "capitals": self.capitals,
            "territory_control_percentage": self.territory_control_percentage,
            "required_continents": self.required_continents,
            "key_areas": self.key_areas,
            "max_rounds": self.max_rounds,
            "turn_time_limit_seconds": self.turn_time_limit_seconds,
            "planning_time_limit_seconds": self.planning_time_limit_seconds,
            "placement_time_limit_seconds": self.placement_time_limit_seconds,
            "placement_reasoning_effort": self.placement_reasoning_effort,
            "planning_reasoning_effort": self.planning_reasoning_effort,
            "attack_reasoning_effort": self.attack_reasoning_effort,
            "fortify_reasoning_effort": self.fortify_reasoning_effort,
            "card_trade_reasoning_effort": self.card_trade_reasoning_effort,
        }
