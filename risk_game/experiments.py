from risk_game.llm_clients import llm_client
import risk_game.game_master as gm
from risk_game.rules import Rules

class Experiment:
    def __init__(self, num_games=10, max_rounds=100, progressive=False, 
                 capitals=False, mode="world_domination"):
        """
        Initialize the experiment with default options.
        
        Args:
        - num_games (int): The number of games to run in the experiment.
        - max_rounds (int): Maximum number of rounds per game.
        - progressive (bool): Whether to use progressive card rules.
        - capitals (bool): Whether to play with capitals.
        - mode (str): Game mode (e.g., "world_domination").
        """
        self.num_games = num_games
        self.max_rounds = max_rounds
        self.progressive = progressive
        self.capitals = capitals
        self.mode = mode
    
    def initialize_game(self):
        """
        Initializes a single game with default rules and players.
        
        Returns:
        - game: An instance of the initialized GameMaster class.
        """
        # Initialize the rules
        rules = Rules(progressive=self.progressive, capitals=self.capitals, 
                      mode=self.mode, max_rounds=self.max_rounds)
        game = gm.GameMaster(rules)
        
        # Add default players
        game.add_player(name="llama3.1_70", 
                        llm_client=llm_client.create_llm_client("Groq", 1))
        game.add_player(name="Claude_Sonnet_3_5", 
                        llm_client=llm_client.create_llm_client("Anthropic", 1))
        game.add_player(name="gpt-4o", 
                        llm_client=llm_client.create_llm_client("OpenAI", 1))

        return game

    def run_experiment(self):
        """
        Runs the experiment by playing multiple games and saving results.
        """
        for i in range(1, self.num_games + 1):
            print(f"Starting game {i}...")
            game = self.initialize_game()
            game.play_game(include_initial_troop_placement=True)
           
