from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np



# Define a function to plot stacked area charts within a FacetGrid
def plot_stacked_area_chart(data,player_colors:dict, **kwargs):
    # This function will be used for each facet to plot the stacked area chart
    game_data = data.pivot(index='Turn_Number', columns='Player_Name', 
                           values='Number_of_Territories')
    
    # Ensure that we fill missing values with 0 for the stacked plot
    game_data = game_data.fillna(0)
    
    plt.stackplot(game_data.index, game_data.T, alpha=0.6, 
        labels=game_data.columns, 
        colors=[player_colors[player] for player in game_data.columns])


def plot_many_stacked_area_charts(troops_and_territory_over_time_df,
                                    player_colors: dict,
                                   experiment_name : str)->None:

    # Set up the FacetGrid for all games
    g = sns.FacetGrid(troops_and_territory_over_time_df, col="Game_Number", 
                      col_wrap=3, height=4, aspect=1.5)

    # Apply the stacked area plot function to each facet
    g.map_dataframe(plot_stacked_area_chart, player_colors=player_colors)

    # Add labels and title
    g.set_axis_labels("Turn Number", "Number of Territories")
    g.figure.suptitle(f"{experiment_name} - Stacked Area Plot - Territory " +
                      f"Control per Turn", y=1.02, size=16)

    # Create a custom legend and place it in the bottom right
    handles, labels = g.axes[0].get_legend_handles_labels()
    g.figure.legend(handles=handles, labels=labels, title="Players", 
        loc="lower right", bbox_to_anchor=(1, 0), 
        bbox_transform=g.figure.transFigure,
        prop={'size': 16}, title_fontsize='16')

    plt.show()


def plot_many_line_plots(troops_and_territory_over_time_df: pd.DataFrame,
                          player_colors: dict, 
                          experiment_name: str) -> None: 
    # 2. Line Plot for Troop Strength for Each Turn
    g2 = sns.FacetGrid(troops_and_territory_over_time_df, col="Game_Number", 
                       col_wrap=3, height=4, aspect=1.5)
    g2.map_dataframe(
        sns.lineplot,
        x="Turn_Number",
        y="Troop_Strength",
        hue="Player_Name",
        palette=player_colors,
        estimator="sum",
        errorbar=None
    )

    # Add a legend and labels
    # g2.add_legend()
    g2.set_axis_labels("Turn Number", "Troop Strength")
    g2.figure.suptitle(
        f"{experiment_name} - Line Plot - Troop Strength per Turn", y=1.02, 
        size=16)
    
    # Create a custom legend and place it in the bottom right
    handles, labels = g2.axes[0].get_legend_handles_labels()
    g2.figure.legend(handles=handles, labels=labels, title="Players", 
        loc="lower right", bbox_to_anchor=(1, 0), 
        bbox_transform=g2.figure.transFigure,
        prop={'size': 16}, title_fontsize='16')

    plt.show()

def plot_average_territory_control(data_df,player_colors:dict, experiment_name: str)->None:   
    """
    Plot the average troop strength per turn for each player across all games, 
    with error bars showing the standard deviation.
    
    Args:
    - data_df: A pandas DataFrame containing the troop strength data for each player at each turn.
    
    Returns:
    - None
    """    
# Step 1: Calculate the mean and half of the standard deviation of troop strength for each player at every turn
    agg_troop_strength_df = data_df.groupby(["Turn_Number", "Player_Name"]).agg(
        Avg_Territory_Control=("Number_of_Territories", "mean"),
        Half_SD_troop_control=("Number_of_Territories", lambda x: x.std() / 2)
    ).reset_index()

    # Step 2: Plot the average troop strength with error bars (1/2 SD) using matplotlib's errorbar function
    plt.figure(figsize=(10, 6))

    # Iterate over each player and plot their troop strength with error bars (1/2 SD)
    for player in player_colors.keys():
        player_data = agg_troop_strength_df[agg_troop_strength_df["Player_Name"] == player]
        plt.errorbar(
            player_data["Turn_Number"], 
            player_data["Avg_Territory_Control"], 
            # yerr=player_data["Half_SD_troop_control"], 
            label=player, 
            color=player_colors[player], 
            fmt='-o'
        )

    # Add labels and title
    plt.title(f"{experiment_name} \nAverage Territory Control per Turn (Across All Games)", fontsize=16)
    plt.xlabel("Turn Number", fontsize=12)
    plt.ylabel("Average Nr. of Controlled Territories", fontsize=12)

    # Add a legend to the bottom right
    plt.legend(title="Players", loc="upper left", fontsize=12, title_fontsize='13')

    plt.tight_layout()
    plt.show()

def plot_average_troop_strength(data_df, player_colors:dict, experiment_name:str)->None:   
    """
    Plot the average troop strength per turn for each player across all games, 
    with error bars showing the standard deviation.
    
    Args:
    - data_df: A pandas DataFrame containing the troop strength data for each player at each turn.
    
    Returns:
    - None
    """    
    # Step 1: Calculate the mean and half of the standard deviation of troop strength for each player at every turn
    agg_troop_strength_df = data_df.groupby(["Turn_Number", "Player_Name"]).agg(
        Avg_Troop_Strength=("Troop_Strength", "mean"),
        Half_Std_Troop_Strength=("Troop_Strength", lambda x: x.std() / 2)
    ).reset_index()

    # Step 2: Plot the average troop strength with error bars (1/2 SD) using matplotlib's errorbar function
    plt.figure(figsize=(10, 6))

    # Iterate over each player and plot their troop strength with error bars (1/2 SD)
    for player in player_colors.keys():
        player_data = agg_troop_strength_df[agg_troop_strength_df["Player_Name"] == player]
        plt.errorbar(
            player_data["Turn_Number"], 
            player_data["Avg_Troop_Strength"], 
            yerr=player_data["Half_Std_Troop_Strength"], 
            label=player, 
            color=player_colors[player], 
            fmt='-o'
        )

    # Add labels and title
    plt.title(f"{experiment_name} \nAverage Troop Strength per Turn (Across All Games) with 1/2 SD Error Bars", fontsize=16)
    plt.xlabel("Turn Number", fontsize=12)
    plt.ylabel("Average Troop Strength", fontsize=12)

    # Add a legend to the bottom right
    plt.legend(title="Players", loc="upper left", fontsize=12, title_fontsize='13')

    plt.tight_layout()
    plt.show()


def plot_errors_over_time(player_data: pd.DataFrame,player_colors:dict ,error_type: str, 
                          experiment_name: str)-> None:
    """
    Plot line charts for different error types over time, averaging over all games played.
    
    Args:
    - player_data (pd.DataFrame): DataFrame containing player data.
    - error_type (str): The column name for the error type to plot.
    """
    plt.figure(figsize=(7, 4))
    
    # Group by Turn_Number and Name to calculate the average error for each player per turn
    avg_errors_df = player_data.groupby(['Turn_Number', 'Name']).agg(
        Avg_Error=(error_type, 'mean')
    ).reset_index()

    # Loop through each player and plot their averaged error evolution over time
    for player in avg_errors_df['Name'].unique():
        player_df = avg_errors_df[avg_errors_df['Name'] == player]
        sns.lineplot(x='Turn_Number', y='Avg_Error', data=player_df, 
                     label=player, color=player_colors[player])

    plt.title(f"{experiment_name} - Average {error_type.replace('_', ' ')} Over Time")
    plt.xlabel("Turn Number")
    plt.ylabel(f"Average {error_type.replace('_', ' ')}")
    plt.legend(title="Players")
    plt.grid(True)
    plt.show()


# def plot_accumulated_turn_time(player_data: pd.DataFrame, player_colors: dict,
#                                          experiment: str)-> None:
#     """
#     Plot line charts for accumulated turn time over time, averaging over all games played.
    
#     Args:
#     - player_data (pd.DataFrame): DataFrame containing player data.
#     """
#     plt.figure(figsize=(7, 4))
    
#     # Group by Turn_Number and Name to calculate the average accumulated turn time for each player per turn
#     avg_turn_time_df = player_data.groupby(['Turn_Number', 'Name']).agg(
#         Avg_Accumulated_Turn_Time=('Accumulated Turn Time', 'mean')
#     ).reset_index()

#     # Loop through each player and plot their averaged accumulated turn time evolution over time
#     for player in avg_turn_time_df['Name'].unique():
#         player_df = avg_turn_time_df[avg_turn_time_df['Name'] == player]
#         sns.lineplot(x='Turn_Number', y='Avg_Accumulated_Turn_Time', data=player_df, 
#                      label=player, color=player_colors[player])

#     plt.title(f"{experiment} - Average Accumulated Turn Time")
#     plt.xlabel("Turn Number")
#     plt.ylabel("Average Accumulated Turn Time (seconds)")
#     plt.legend(title="Players")
#     plt.grid(True)
#     plt.show()


# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np

# def plot_accumulated_turn_time(player_data: pd.DataFrame, player_colors: dict, experiment: str) -> None:
#     """
#     Plot line charts for accumulated turn time over time, averaging over all games played.
    
#     Args:
#     - player_data (pd.DataFrame): DataFrame containing player data.
#     - player_colors (dict): Dictionary mapping player names to colors.
#     - experiment (str): Experiment name or title for the plot.
#     """
#     plt.figure(figsize=(7, 4))
    
#     # Convert missing or invalid values in 'Accumulated Turn Time' to NaN
#     player_data['Accumulated Turn Time'] = player_data['Accumulated Turn Time'].replace([None, np.nan], np.nan)

#     # Group by Turn_Number and Name to calculate the average accumulated turn time for each player per turn
#     avg_turn_time_df = player_data.groupby(['Turn_Number', 'Name']).agg(
#         Avg_Accumulated_Turn_Time=('Accumulated Turn Time', 'mean')
#     ).reset_index()

#     # Loop through each player and plot their averaged accumulated turn time evolution over time
#     for player in avg_turn_time_df['Name'].unique():
#         player_df = avg_turn_time_df[avg_turn_time_df['Name'] == player]
#         sns.lineplot(x='Turn_Number', y='Avg_Accumulated_Turn_Time', data=player_df, 
#                      label=player, color=player_colors.get(player, 'black'))  # Use black if player color is missing

#     plt.title(f"{experiment} - Average Accumulated Turn Time")
#     plt.xlabel("Turn Number")
#     plt.ylabel("Average Accumulated Turn Time (seconds)")
#     plt.legend(title="Players")
#     plt.grid(True)
#     plt.show()



# def plot_accumulated_turn_time(player_data: pd.DataFrame, player_colors: dict, experiment: str) -> None:
#     """
#     Plot line charts for accumulated turn time over time, averaging over all games played.
    
#     Args:
#     - player_data (pd.DataFrame): DataFrame containing player data.
#     - player_colors (dict): Dictionary mapping player names to colors.
#     - experiment (str): Experiment name or title for the plot.
#     """
#     plt.figure(figsize=(7, 4))
    
#     # Convert missing or invalid values in 'Accumulated Turn Time' to NaN
#     player_data['Accumulated Turn Time'] = player_data['Accumulated Turn Time'].replace([None, np.nan], np.nan)

#     # Ensure the data is sorted by Game_Number and Turn_Number to maintain the correct order
#     player_data = player_data.sort_values(by=['Game_Number', 'Turn_Number'])
    
#     # Group by Game_Number, Turn_Number, and Name to calculate the average accumulated turn time for each player per turn
#     avg_turn_time_df = player_data.groupby(['Game_Number', 'Turn_Number', 'Name']).agg(
#         Avg_Accumulated_Turn_Time=('Accumulated Turn Time', 'mean')
#     ).reset_index()

#     # Loop through each player and plot their averaged accumulated turn time evolution over time
#     for player in avg_turn_time_df['Name'].unique():
#         player_df = avg_turn_time_df[avg_turn_time_df['Name'] == player]
        
#         # Plot each player's accumulated turn time for each game separately
#         sns.lineplot(x='Turn_Number', y='Avg_Accumulated_Turn_Time', hue='Game_Number', data=player_df, 
#                      palette=sns.color_palette("husl", len(player_df['Game_Number'].unique())))
    
#     plt.title(f"{experiment} - Average Accumulated Turn Time (by Game)")
#     plt.xlabel("Turn Number")
#     plt.ylabel("Average Accumulated Turn Time (seconds)")
#     plt.legend(title="Players")
#     plt.grid(True)
#     plt.show()


# this one works but plots it by game.. not reall what we want
# def plot_accumulated_turn_time(player_data: pd.DataFrame, player_colors: dict, experiment: str) -> None:
#     """
#     Plot line charts for accumulated turn time over time, averaging over all games played.
    
#     Args:
#     - player_data (pd.DataFrame): DataFrame containing player data.
#     - player_colors (dict): Dictionary mapping player names to colors.
#     - experiment (str): Experiment name or title for the plot.
#     """
#     plt.figure(figsize=(7, 4))
    
#     # Convert missing or invalid values in 'Accumulated Turn Time' to NaN
#     player_data['Accumulated Turn Time'] = player_data['Accumulated Turn Time'].replace([None, np.nan], np.nan)

#     # Ensure the data is sorted by Game_Number and Turn_Number to maintain the correct order
#     player_data = player_data.sort_values(by=['Game_Number', 'Turn_Number'])
    
#     # Group by Game_Number, Turn_Number, and Name to calculate the average accumulated turn time for each player per turn
#     avg_turn_time_df = player_data.groupby(['Game_Number', 'Turn_Number', 'Name']).agg(
#         Avg_Accumulated_Turn_Time=('Accumulated Turn Time', 'mean')
#     ).reset_index()

#     # Plot all players' accumulated turn time evolution over time, with hue set to Game_Number
#     sns.lineplot(x='Turn_Number', y='Avg_Accumulated_Turn_Time', hue='Game_Number', data=avg_turn_time_df, 
#                  palette=sns.color_palette("husl", len(avg_turn_time_df['Game_Number'].unique())))

#     # Adjust the legend
#     plt.title(f"{experiment} - Average Accumulated Turn Time (by Game)")
#     plt.xlabel("Turn Number")
#     plt.ylabel("Average Accumulated Turn Time (seconds)")
#     plt.legend(title="Games")  # Change the legend title to "Games"
#     plt.grid(True)
#     plt.show()



def plot_accumulated_turn_time(player_data: pd.DataFrame, player_colors: dict, experiment: str) -> None:
    """
    Plot line charts for accumulated turn time over time, averaging over all games played.
    
    Args:
    - player_data (pd.DataFrame): DataFrame containing player data.
    - player_colors (dict): Dictionary mapping player names to colors.
    - experiment (str): Experiment name or title for the plot.
    """
    plt.figure(figsize=(7, 4))
    
    # Convert missing or invalid values in 'Accumulated Turn Time' to NaN
    player_data['Accumulated Turn Time'] = player_data['Accumulated Turn Time'].replace([None, np.nan], np.nan)

    # Ensure the data is sorted by Turn_Number and Name to maintain the correct order
    player_data = player_data.sort_values(by=['Turn_Number', 'Name'])
    
    # Group by Turn_Number and Name to calculate the average accumulated turn time across all games for each player
    avg_turn_time_df = player_data.groupby(['Turn_Number', 'Name']).agg(
        Avg_Accumulated_Turn_Time=('Accumulated Turn Time', 'mean')
    ).reset_index()

    # Loop through each player and plot their average accumulated turn time over time
    for player in avg_turn_time_df['Name'].unique():
        player_df = avg_turn_time_df[avg_turn_time_df['Name'] == player]
        
        # Plot each player's accumulated turn time
        sns.lineplot(x='Turn_Number', y='Avg_Accumulated_Turn_Time', data=player_df, 
                     label=player, color=player_colors.get(player, 'black'))  # Use black if player color is missing

    plt.title(f"{experiment} - Average Accumulated Turn Time by Player")
    plt.xlabel("Turn Number")
    plt.ylabel("Average Accumulated Turn Time (seconds)")
    plt.legend(title="Players")  # Adjust the legend title to "Players"
    plt.grid(True)
    plt.show()



  





def plot_wins_by_victory_condition(df: pd.DataFrame,player_colors:dict,
                                    experiment_name: str) -> None:
    """
    Creates a seaborn grouped bar plot showing the number of wins by player, grouped by victory condition.
    
    Args:
    - df (pd.DataFrame): The DataFrame containing the experiment results. It should have columns 'winner', 
                         'victory_condition', and any other relevant columns.
    
    Returns:
    - None: This function directly displays the plot.
    """
    
    # Count the number of wins by victory_condition and winner
    win_counts = df.groupby(['victory_condition', 'winner']).size().reset_index(name='count')

    # Plotting with seaborn
    plt.figure(figsize=(8, 6))
    sns.set_theme(style="whitegrid")

    # Create a seaborn barplot with the custom color palette
    ax = sns.barplot(x='victory_condition', y='count', hue='winner', data=win_counts, palette=player_colors)

    # Add title and labels
    ax.set_title(f'{experiment_name} - Number of Wins by Player Grouped by Victory Condition')
    ax.set_xlabel('Victory Condition')
    ax.set_ylabel('Number of Wins')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=0, ha='center')

    # Show the plot
    plt.tight_layout()
    plt.show()

# Example usage (assuming df contains the necessary data):
# plot_wins_by_victory_condition(df, experiment_name="Your Experiment")



################################## heatmap stuff

def create_ownership_df(df:pd.DataFrame, game_number:int) -> pd.DataFrame:  

    # Assuming df is your original DataFrame containing the game data

    # Step 1: Filter data for a specific game, e.g., Game 1
    game_df = df[df["Game_Number"] == game_number]

    non_player_names = ["Territory","Turn_Number","Game_Round","Game_Number"]
    player_names = [col for col in game_df.columns if col not in non_player_names]

    # Step 2: Melt the DataFrame to long format
    melted_df = pd.melt(game_df, id_vars=["Territory", "Turn_Number", "Game_Number"], 
                        value_vars=player_names, 
                        var_name="Player_Name", value_name="Troops")

    # Step 3: Filter out rows where Troops == 0 (i.e., player does not control the territory)
    ownership_df = melted_df[melted_df["Troops"] > 0]

    # Step 4: Drop the 'Troops' column, as we only need 'Territory', 'Turn_Number', and 'Player_Name' for ownership
    ownership_df = ownership_df.drop(columns=["Troops"])

    # Now ownership_df contains the data showing which player owns each territory at each turn for the selected game
    return ownership_df

def prepare_heatmap_data(ownership_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares the data for a heatmap of territory ownership over time.
    
    Args:
    - ownership_df (pd.DataFrame): DataFrame showing which player owns each territory at each turn.
    
    Returns:
    - pd.DataFrame: Pivoted DataFrame with territories as rows, turns as columns, and player ownership as values.
    """
    # Pivot the DataFrame to get territories as rows, turns as columns, and player ownership as values
    heatmap_data = ownership_df.pivot(index='Territory', columns='Turn_Number', values='Player_Name')
    
    return heatmap_data

def map_players_to_numeric_with_colors(heatmap_data: pd.DataFrame, player_colors: dict
                                       ) -> (pd.DataFrame, dict, list):
    """
    Maps player labels to numeric values for heatmap plotting and associates them with colors.
    
    Args:
    - heatmap_data (pd.DataFrame): DataFrame with player labels.
    - player_colors (dict): Dictionary mapping player labels to colors.
    
    Returns:
    - pd.DataFrame: DataFrame with numeric values instead of player labels.
    - dict: Dictionary mapping numeric values to player labels.
    - list: List of colors corresponding to the numeric mapping.
    """
    unique_players = sorted(heatmap_data.stack().unique())  # Get unique player labels
    player_to_numeric = {player: idx + 1 for idx, player in enumerate(unique_players)}
    
    # Create a list of colors matching the numeric player labels
    colors = [player_colors[player] for player in unique_players]
    
    # Replace player labels with numeric values
    numeric_heatmap_data = heatmap_data.replace(player_to_numeric)
    
    return numeric_heatmap_data, player_to_numeric, colors

def plot_continent_heatmaps(ownership_df: pd.DataFrame, continent_mapping: dict, player_to_numeric: dict, colors: list, title: str):
    """
    Plots separate heatmaps for each continent with whitespace between continents,
    and adjusts the vertical space allocated to each continent based on the number of territories.
    
    Args:
    - ownership_df (pd.DataFrame): DataFrame showing which player owns each territory at each turn.
    - continent_mapping (dict): Dictionary that maps continents to their territories.
    - player_to_numeric (dict): Dictionary mapping numeric values to player labels.
    - colors (list): List of colors corresponding to player numeric values.
    - title (str): Title for the entire plot.
    """
    num_continents = len(continent_mapping)
    
    # Calculate height ratios based on the number of territories in each continent
    height_ratios = [len(territories) for territories in continent_mapping.values()]
    
    fig, axes = plt.subplots(num_continents, 1, figsize=(20, 0.28 * sum(height_ratios)), 
                             sharex=True, gridspec_kw={'height_ratios': height_ratios})
    
    if num_continents == 1:
        axes = [axes]  # Ensure axes is always a list even if there's only one continent

    for ax, (continent, territories) in zip(axes, continent_mapping.items()):
        # Filter the ownership DataFrame for the current continent's territories
        continent_df = ownership_df[ownership_df['Territory'].isin(territories)]
        
        # Pivot the DataFrame to prepare the heatmap data
        heatmap_data = continent_df.pivot(index='Territory', columns='Turn_Number', values='Player_Name')
        
        # Replace player names with numeric values
        numeric_heatmap_data = heatmap_data.replace(player_to_numeric)
        
        # Plot the heatmap for the current continent
        sns.heatmap(data=numeric_heatmap_data, cmap=sns.color_palette(colors), cbar=False, linewidths=0.5, ax=ax)
        ax.set_title(f"Territory Ownership - {continent}")
        ax.set_xlabel("Turn")
        ax.set_ylabel("")
        
        # Rotate the y-axis labels to be horizontal
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    # Add a title to the entire plot
    plt.suptitle(title, fontsize=20)
    
    # Create a custom legend for the players
    legend_labels = [f"Player {player}" for player in player_to_numeric.keys()]
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[idx]) for idx in range(len(player_to_numeric))]
    plt.legend(handles, legend_labels, title="Players", bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to make room for the title
    plt.show()

# Example usage:
# plot_continent_heatmaps(df, continent_mapping, player_to_numeric, colors, title="Risk Game Territory Ownership")





def creat_full_heatmap_plot(input_df:pd.DataFrame, continent_mapping:dict, player_colors:dict, game_number:int, title:str):    
    
    df = create_ownership_df(input_df, game_number)
    # Example usage:
    # df is the ownership DataFrame which contains columns: 'Territory', 'Turn_Number', and 'Player_Name'
    # continent_mapping is the dictionary mapping continents to their respective territories
    # player_colors is a dictionary mapping player names to colors

    # Prepare heatmap data
    heatmap_data = prepare_heatmap_data(df)

    # Map player labels to numeric values and get corresponding colors
    numeric_heatmap_data, player_to_numeric, colors = map_players_to_numeric_with_colors(heatmap_data, player_colors)

    # Plot continent heatmaps
    plot_continent_heatmaps(df, continent_mapping, player_to_numeric, colors, title=f"{title} - Game {game_number} - Territory Ownership")