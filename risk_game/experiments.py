from risk_game.llm_clients import llm_client
import risk_game.game_master as gm
from risk_game.rules import Rules
from typing import List
from risk_game.game_config import GameConfig 

class Experiment:
    def __init__(self, config: GameConfig, agent_mix: int= 1, num_games=10
      ) -> None:
        """
        Initialize the experiment with default options.
        
        Args:
        - num_games (int): The number of games to run in the experiment.
        - agent_mix (int): The type of agent mix to use in the experiment.
        - config (GameConfig): The configuration for the game.

        """
        self.config = config    
        self.num_games = num_games
        self.agent_mix = agent_mix

    def __repr__(self) -> str:

        if self.config.key_areas:
            key_areas = ', '.join(self.config.key_areas)
        else:
            key_areas = 'None'

        return (f"Experiment Configuration:\n"
                f"Agent Mix: {self.agent_mix}\n"
                f"Number of Games: {self.num_games}\n"
                f"Progressive: {self.config.progressive}\n"
                f"Capitals: {self.config.capitals}\n"
                f"Territory Control Percentage: +"
                f"{self.config.territory_control_percentage:.2f}\n"
                f"Required Continents: {self.config.required_continents}\n"
                f"Key Areas: {key_areas}\n"
                f"Max Rounds: {self.config.max_rounds}\n")
    
    def initialize_game(self)-> gm.GameMaster:
        """
        Initializes a single game with default rules and players.
        
        Returns:
        - game: An instance of the initialized GameMaster class.
        """
        # Initialize the rules
        rules = Rules(self.config)
        game = gm.GameMaster(rules)
        
        if self.agent_mix == 1:
            # Add strong AI players
            game.add_player(name="llama3.1_70", 
                        llm_client=llm_client.create_llm_client("Groq", 1))
            game.add_player(name="Claude_Sonnet_3_5", 
                        llm_client=llm_client.create_llm_client("Anthropic", 1))
            game.add_player(name="gpt-4o", 
                        llm_client=llm_client.create_llm_client("OpenAI", 1))
        
        elif self.agent_mix == 3:
            # Add mix of strong and weaker AI players from Open AI
            game.add_player(name="Strong(gpt-4o)", 
                        llm_client=llm_client.create_llm_client("OpenAI", 1))
            game.add_player(name="Medium(gpt-4o-mini)", 
                        llm_client=llm_client.create_llm_client("OpenAI", 2))
            game.add_player(name="Weak(gpt-3.5-turbo)", 
                        llm_client=llm_client.create_llm_client("OpenAI", 3))

        elif self.agent_mix == 5:
            # Add mix extra strong AI players
            game.add_player(name="Big_llama3.1_400", 
                        llm_client=llm_client.create_llm_client("Bedrock", 1))
            game.add_player(name="Claude_Sonnet_3_5", 
                        llm_client=llm_client.create_llm_client("Anthropic", 1))
            game.add_player(name="gpt-4o", 
                        llm_client=llm_client.create_llm_client("OpenAI", 1))
          


        return game

    def run_experiment(self)-> None:
        """
        Runs the experiment by playing multiple games and saving results.
        """
        for i in range(1, self.num_games + 1):
            print(f"Starting game {i}...")
            game = self.initialize_game()
            game.play_game(include_initial_troop_placement=True)
           
