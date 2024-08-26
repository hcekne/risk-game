# Risk Game AI

## Overview
This project implements a simplified version of the Risk board game with AI players.

The AI players play against each other using the API of the respective LLMs.



## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/hcekne/risk-game.git
   cd risk-game
   ```

2. **Add API keys to .env file:**

   Set the values of the  API to match your own
   Rename the .env.examples file
   ```bash
   mv .env.examples .env
   ```
   Edit the .env file and insert your own keys
   ```bash
   nano .env
   ```


3. **Create the dev container to run the code:**
   ```bash
   . start_container.sh
   ```
4. **Enter into the container:**
   ```bash
   docker exec -it risk-game-container bash
   ```

## Running the Game
To run the game, execute the following command inside the container:
```bash
python scripts/example_run.py
```

## Running Tests
To run the tests, use the following command:
```bash
pytest tests/
```

## Contributing
Feel free to submit issues or pull requests.


## TODO
- [ ] Task 0: Implement Game history
- [ ] Task 4: Add tests to the project
- [ ] Task 6: Consider creating a better way to follow games and watch the players
- [ ] Task 7: Create pixelated map of the risk world
- [ ] Task 8: Create some dashboard where you can look through game states
- [ ] Task 9: Consider adding in different agents with more enhanced and stratgic prompts




