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
To run the game, execute the following command:
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
- [ ] Task 1: add open AI gpt 4-0 player
- [ ] Task 2: add llama3.1 405 b player
- [ ] Task 3: consider another top model anthropic????
- [ ] Task 4: Create pixelated map of the risk world
- [ ] Task 5: Create some dashboard where you can look through game states

### Gamelogic outline:

1. Initialize all the players you want to have
2. Initialize the game
3. Determine randomly the order of the players (maybe shuffle the list? and the first on the list goes first??)
4. Ask how you want to do the troop placement.. Default is all troops are randomly placed on the board until each territory has 1 troop on it. You can have a function that does this. (based on the number of players divide numbers 1-42 amongst them randomly so that they are evenly distributed.)

4.b this step could also be done so that the agents each choose where to put their troops from an empty board until all territories have 1 troop on them.

5. Now the remaining troops need to be placed. Continue with the player whos turn it would be in the random placement steps and this player is now given the game state and asked to place a troop on any of his territories. 
6. The player suggest where to place 1 troop and responds with the new game state to the gamemaster, in addition to the name of the territory the new troop was placed
7. The game master checks if  the old game state is incremented by one troop in the territory that the agent suggested and if so updates the game state. This continues until all players have 0 troops left to place. 

---

All troops are now deployed and the game can start. We use the previously determined player order to determined play.


8. Start Game: The game master starts play. The first player is given the current game state, and extra troops based on his territories and other bonuses. The turn is then based around 3 steps:

8.a the player is given the game state, his cards that he has collected and the bonus troops he recieves.If the player has 5 cards he must trade in 3 cards. If the player has 3 or 4 cards he can choose to trade the cards for troops. The player then receives the extra troops based on the cards. (there is one card for each territory in addition to 5 wildcards.) (the game master needs to keep track of how many cards there are left, there needs to be two stacks of cards, one for discarded and one for to be used.) The player then chooses troop allocation and returns the new game state to the game master. The game master checks the troop allocation (only on player territories and number of totally added troops match how many the player had available.)
8.b If the player placed troops correctly he can now start his attack phase. He will choose which territory to attack and with how many troops. The game master then reviews this and checks if the move is legal (enough troops to be able to attack etc.) and then calulcates the outcome. The game master then updates the game state and returns the game state to the player. This continues until the player doesn't want to attack any more or until 20 seconds have elapsed.???? So this means the attack phase can be a loop. (if a player is elimnated during this phase the player is removed from players and added to dead players. If there is only one player left then the game is over.)
8.c now we get to the movement phase. the game master sends the game state to the player and the player then moves and returns a new game state to the game master. If the game state is correct the game master updates the game state. And it's the next players turn.

Extra notes: the game state can exist as a numpy array? does that make sense?



