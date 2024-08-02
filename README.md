# Risk Game AI

## Overview
This project implements a simplified version of the Risk board game with AI players.

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
To run the game, execute the following command:
```bash
python scripts/run_game.py
```

## Running Tests
To run the tests, use the following command:
```bash
pytest tests/
```

## Contributing
Feel free to submit issues or pull requests.


## TODO
- [ ] Task 0: Write game logic outline
- [ ] Task 1: Progam Game master and game logic
- [ ] Task 2: Progam rules
- [ ] Task 3: Add in API keys
- [ ] Task 4: Create pixelated map of the risk world
- [ ] Task 5: Create some dashboard where you can look through game states

### Gamelogic outline:

1. Initialize all the players you want to have
2. start the game
3. Determine randomly the order of the players (maybe shuffle the list? and the first on the list goes first??)
4. Ask how you want to do the troop placement.. Default is all troops are randomly placed on the board until each territory has 1 troop on it. You can have a function that does this. (based on the number of players divide numbers 1-42 amongst them randomly so that they are evenly distributed.)

4.b this step could also be done so that the agents each choose where to put their troops from an empty board until all territories have 1 troop on them.

5. Now the remaining troops need to be placed. Continue with the player whos turn it would be in the random placement steps and this player is now given the game state and asked to place a troop on any of his territories. 
6. The player suggest where to place 1 troop and responds with the new game state to the gamemaster, in addition to the name of the territory the new troop was placed
7. The game master checks if  the old game state is incremented by one troop in the territory that the agent suggested and if so updates the game state. This continues until all players have 0 troops left to place. 


