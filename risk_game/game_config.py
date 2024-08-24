from typing import List, Dict, Any

class GameConfig:
    def __init__(self, 
                 progressive: bool = True, 
                 capitals: bool = False, 
                 territory_control_percentage: float = 0.65, 
                 required_continents: int = 0, 
                 key_areas: List[str] = None, 
                 max_rounds: int = 15) -> None:
        self.progressive = progressive
        self.capitals = capitals
        self.territory_control_percentage = territory_control_percentage
        self.required_continents = required_continents
        self.key_areas = key_areas or []
        self.max_rounds = max_rounds

    def to_dict(self) -> Dict[str, Any]:
        return {
            "progressive": self.progressive,
            "capitals": self.capitals,
            "territory_control_percentage": self.territory_control_percentage,
            "required_continents": self.required_continents,
            "key_areas": self.key_areas,
            "max_rounds": self.max_rounds
        }