import os
import pandas as pd
import re
import json
import math

# Provided function
def load_game_state_from_folder(game_folder: str) -> pd.DataFrame:
    """
    Load all game state CSV files from a folder into a single DataFrame.
    
    Args:
    - game_folder (str): The path to the folder containing the 
        game state CSV files.
    
    Returns:
    - pd.DataFrame: A DataFrame containing all the game state data.
    """
    # Regex pattern to match game state files
    pattern = re.compile(r"game_state_turn_(\d+)\.csv")
    
    # List to store individual turn data
    game_states = []
    
    # Loop through files in the folder
    for filename in os.listdir(game_folder):
        # Check if the filename matches the pattern
        match = pattern.match(filename)
        if match:
            # Extract the turn number from the filename
            turn_number = int(match.group(1))
            # Load the CSV file into a DataFrame
            filepath = os.path.join(game_folder, filename)
            turn_df = pd.read_csv(filepath)
            # Add the turn number to the DataFrame
            turn_df['Turn_Number'] = turn_number
            # Append the DataFrame to the list
            game_states.append(turn_df)
    
    # Concatenate all DataFrames into a single DataFrame
    full_game_state_df = pd.concat(game_states, ignore_index=True)
    
    return full_game_state_df

def load_player_data_from_folder(game_folder: str) -> pd.DataFrame:
    """
    Load all player data CSV files from a folder into a single DataFrame,
    and remove the 'Troops' column.
    
    Args:
    - game_folder (str): The path to the folder containing the 
        player data CSV files.
    
    Returns:
    - pd.DataFrame: A DataFrame containing all the player data (without the 'Troops' column).
    """
    # Regex pattern to match player data files
    pattern = re.compile(r"player_data_turn_(\d+)\.csv")
    
    # List to store individual turn data
    player_data = []
    
    # Loop through files in the folder
    for filename in os.listdir(game_folder):
        # Check if the filename matches the pattern
        match = pattern.match(filename)
        if match:
            # Extract the turn number from the filename
            turn_number = int(match.group(1))
            # Load the CSV file into a DataFrame
            filepath = os.path.join(game_folder, filename)
            turn_df = pd.read_csv(filepath)
            # Drop the 'Troops' column if it exists
            if 'Troops' in turn_df.columns:
                turn_df = turn_df.drop(columns=['Troops'])
            # Add the turn number to the DataFrame
            turn_df['Turn_Number'] = turn_number
            # Append the DataFrame to the list
            player_data.append(turn_df)
    
    # Concatenate all DataFrames into a single DataFrame
    full_player_data_df = pd.concat(player_data, ignore_index=True)
    
    return full_player_data_df

def process_json_files_in_folder(folder_path: str) -> pd.DataFrame:
    """
    Process all JSON files in a folder and compile their data into a DataFrame.
    
    Args:
    - folder_path (str): The path to the folder containing JSON files.
    
    Returns:
    - pd.DataFrame: A DataFrame containing the extracted data from all JSON files.
    """
    game_summaries = []
    

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):  # Process only JSON files
            file_path = os.path.join(folder_path, filename)
            game_summary = extract_game_summary_from_json(file_path)
            game_summaries.append(game_summary)
    
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(game_summaries)
    
    return df

def extract_game_summary_from_json(json_file: str) -> dict:
    """
    Extract relevant fields from a JSON file.
    
    Args:
    - json_file (str): The path to the JSON file.
    
    Returns:
    - dict: A dictionary containing the extracted fields.
    """
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Extract the required fields
    game_summary = {
        'winner': data.get('winner'),
        'victory_condition': data.get('victory_condition'),
        'total_rounds': data.get('total_rounds')
    }
    
    return game_summary

def combine_game_results(func, base_folder: str) -> pd.DataFrame:
    """
    Combine game results from all subfolders within the base folder.
    
    Args:
    - base_folder (str): The path to the base folder containing game subfolders.
    
    Returns:
    - pd.DataFrame: A DataFrame containing all the combined game state data.
    """
    combined_df = pd.DataFrame()  # Initialize an empty DataFrame
    folder_number = 0  # Initialize folder counter

    # Loop through each subfolder in the base folder
    for folder_name in os.listdir(base_folder):
        game_folder = os.path.join(base_folder, folder_name)
        
        if os.path.isdir(game_folder):  # Check if it's a directory
            folder_number += 1  # Increment folder counter
            
            # Load the game state data from the folder
            full_game_state_df = func(game_folder)
            
            # Add a column indicating the folder number
            full_game_state_df['Game_Number'] = folder_number
            
            # Append the game state DataFrame to the combined DataFrame
            combined_df = pd.concat([combined_df, full_game_state_df], ignore_index=True)
    
    return combined_df

def binomial_coefficient(n, k):
    """Calculate the binomial coefficient (n choose k)."""
    return math.comb(n, k)

def binomial_probability(n, k, p):
    """Calculate the binomial probability P(X = k) for a given number of trials n and success probability p."""
    binom_coeff = binomial_coefficient(n, k)
    return binom_coeff * (p ** k) * ((1 - p) ** (n - k))

def binomial_test_p_value(n, p_null, x_observed):
    """
    Calculate the p-value for observing X >= x_observed under the binomial distribution with n trials and
    probability of success p_null.
    """
    # Sum the probabilities of observing x_observed or more successes
    p_value = sum(binomial_probability(n, k, p_null) for k in range(x_observed, n + 1))
    return p_value

# # Parameters for the binomial test
# n = 10  # number of trials (games)
# p_null = 1/3  # probability of success under H0
# x_observed = 7  # observed number of successes (wins)

# # Calculate the p-value for X >= 8 under the binomial distribution
# p_value = binomial_test_p_value(n, p_null, x_observed)
# p_value


def calculate_troop_strength_over_time(game_state_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the troop strength for each player over time for each game.
    
    Args:
    - game_state_df (pd.DataFrame): The full game state DataFrame with a 'Game_Number' column.
    
    Returns:
    - pd.DataFrame: A DataFrame showing the troop strength of each player at each turn for each game.
    """
    # Columns that are not player names
    non_player_columns = {'Territory', 'Turn_Number', 'Game_Round', 'Game_Number'}

    # Extract the player names by excluding non-player columns
    player_columns = [col for col in game_state_df.columns if col not in non_player_columns]
    
    # Initialize an empty list to store DataFrames for each game
    all_games_troop_strength = []

    # Loop through each game
    for game_number in sorted(game_state_df['Game_Number'].unique()):
        # Filter the DataFrame for the current game
        game_df = game_state_df[game_state_df['Game_Number'] == game_number]
        
        # Initialize an empty dictionary to store data for the current game
        data_on_troops = {'Turn': [], 'Game_Number': []}
        
        # Loop through each turn and calculate the troop strength
        for turn_number in sorted(game_df['Turn_Number'].unique()):
            data_on_troops['Turn'].append(turn_number)
            data_on_troops['Game_Number'].append(game_number)
            
            turn_df = game_df[game_df['Turn_Number'] == turn_number]
            
            for player in player_columns:
                total_troops = turn_df[player].sum()  # Sum the troop counts for the player
                if player not in data_on_troops:
                    data_on_troops[player] = []
                data_on_troops[player].append(total_troops)
        
        # Convert the dictionary for this game to a DataFrame
        troop_strength_df = pd.DataFrame(data_on_troops)
        
        # Append the DataFrame for this game to the list
        all_games_troop_strength.append(troop_strength_df)
    
    # Concatenate all the individual game DataFrames into one large DataFrame
    combined_troop_strength_df = pd.concat(all_games_troop_strength, ignore_index=True)
    
    return combined_troop_strength_df

import pandas as pd


def calculate_territory_control_over_time(game_state_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the number of territories controlled by each player over time for each game.territory_troop_control_over_time
    
    Args:
    - game_state_df (pd.DataFrame): The full game state DataFrame with a 'Game_Number' column.
    
    Returns:
    - pd.DataFrame: A DataFrame showing the number of territories controlled by each player at each turn for each game.
    """
    # Columns that are not player names
    non_player_columns = {'Territory', 'Turn_Number', 'Game_Round', 'Game_Number'}
    
    # Extract the player names by excluding non-player columns
    player_columns = [col for col in game_state_df.columns if col not in non_player_columns]
    
    # Convert player columns to numeric (in case they contain non-numeric data)
    game_state_df[player_columns] = game_state_df[player_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Initialize an empty list to store DataFrames for each game
    all_games_territory_control = []

    # Loop through each game
    for game_number in sorted(game_state_df['Game_Number'].unique()):
        # Filter the DataFrame for the current game
        game_df = game_state_df[game_state_df['Game_Number'] == game_number]
        
        # Initialize an empty dictionary to store data for the current game
        data_on_territories = {'Turn': [], 'Game_Number': []}
        
        # Loop through each turn and calculate the territory control
        for turn_number in sorted(game_df['Turn_Number'].unique()):
            data_on_territories['Turn'].append(turn_number)
            data_on_territories['Game_Number'].append(game_number)
            
            turn_df = game_df[game_df['Turn_Number'] == turn_number]
            
            for player in player_columns:
                # Count the number of territories controlled (i.e., where troop count is greater than 0)
                territories_controlled = (turn_df[player] > 0).sum()
                if player not in data_on_territories:
                    data_on_territories[player] = []
                data_on_territories[player].append(territories_controlled)
        
        # Convert the dictionary for this game to a DataFrame
        territory_control_df = pd.DataFrame(data_on_territories)
        
        # Append the DataFrame for this game to the list
        all_games_territory_control.append(territory_control_df)
    
    # Concatenate all the individual game DataFrames into one large DataFrame
    combined_territory_control_df = pd.concat(all_games_territory_control, ignore_index=True)
    
    return combined_territory_control_df


def calculate_territory_ownership(game_state_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate territory ownership over time for each player for each game.
    
    Args:
    - game_state_df (pd.DataFrame): The full game state DataFrame, which includes a 'Game_Number' column.
    
    Returns:
    - pd.DataFrame: A DataFrame showing which player owns each territory at each turn for each game.
    """
    # Columns that are not player names
    non_player_columns = {'Territory', 'Turn_Number', 'Game_Round', 'Game_Number'}
    
    # Extract the player names by excluding non-player columns
    player_columns = [col for col in game_state_df.columns if col not in non_player_columns]
    
    # Melt the DataFrame to have a row for each player-territory combination per turn, including 'Game_Number'
    melted_df = game_state_df.melt(id_vars=['Territory', 'Turn_Number', 'Game_Number'],
                                   value_vars=player_columns,
                                   var_name='Player', value_name='Troops')
    
    # Filter to only include territories where a player has troops (i.e., ownership)
    owned_territories_df = melted_df[melted_df['Troops'] > 0].copy()
    
    # Drop the 'Troops' column, as we only care about ownership
    owned_territories_df = owned_territories_df.drop(columns=['Troops'])
    
    return owned_territories_df

# Used in the new algorithm
def territory_troop_control_over_time(data_df):

    df = data_df.copy()

    df.drop(columns=["Game_Round"], inplace=True)

    cols = ["Territory", "Turn_Number", "Game_Number"]
    player_cols = [col for col in df.columns if "player" not in cols]

    # Melting the DataFrame to have Player_Name and Troop Strength as separate columns
    melted_df = df.melt(
        id_vars=["Turn_Number", "Game_Number", "Territory"],
        value_vars=player_cols,
        var_name="Player_Name",
        value_name="Troop_Strength"
    )

    # Calculating the number of territories controlled and the total troop strength for each player per turn and game
    summarized_df = melted_df.groupby(["Player_Name", "Turn_Number", "Game_Number"]).agg(
        Troop_Strength=('Troop_Strength', 'sum'),
        Number_of_Territories=('Troop_Strength', lambda x: (x > 0).sum())
    ).reset_index()

    return summarized_df
