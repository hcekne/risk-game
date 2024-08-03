# utils.py

TERRITORIES = [
    "Alaska", "Northwest Territory", "Greenland", "Alberta", "Ontario", "Quebec", 
    "Western United States", "Eastern United States", "Central America", "Venezuela", 
    "Peru", "Brazil", "Argentina", "North Africa", "Egypt", "East Africa", 
    "Congo", "South Africa", "Madagascar", "Western Europe", "Southern Europe", 
    "Northern Europe", "Great Britain", "Iceland", "Scandinavia", "Ukraine", 
    "Afghanistan", "Ural", "Siberia", "Yakutsk", "Kamchatka", "Irkutsk", 
    "Mongolia", "Japan", "China", "India", "Siam", "Indonesia", "New Guinea", 
    "Western Australia", "Eastern Australia", "Middle East"
]

# Define the connections between territories
TERRITORY_CONNECTIONS = {
    "Alaska": ["Northwest Territory", "Alberta", "Kamchatka"],
    "Northwest Territory": ["Alaska", "Alberta", "Ontario", "Greenland"],
    "Greenland": ["Northwest Territory", "Ontario", "Quebec", "Iceland"],
    "Alberta": ["Alaska", "Northwest Territory", "Ontario", "Western United States"],
    "Ontario": ["Northwest Territory", "Greenland", "Quebec", "Alberta", "Western United States", "Eastern United States"],
    "Quebec": ["Greenland", "Ontario", "Eastern United States"],
    "Western United States": ["Alberta", "Ontario", "Eastern United States", "Central America"],
    "Eastern United States": ["Ontario", "Quebec", "Western United States", "Central America"],
    "Central America": ["Western United States", "Eastern United States", "Venezuela"],
    "Venezuela": ["Central America", "Peru", "Brazil"],
    "Peru": ["Venezuela", "Brazil", "Argentina"],
    "Brazil": ["Venezuela", "Peru", "Argentina", "North Africa"],
    "Argentina": ["Peru", "Brazil"],
    "North Africa": ["Brazil", "Egypt", "East Africa", "Congo", "Western Europe", "Southern Europe"],
    "Egypt": ["North Africa", "East Africa", "Southern Europe", "Middle East"],
    "East Africa": ["Egypt", "North Africa", "Congo", "South Africa", "Madagascar", "Middle East"],
    "Congo": ["North Africa", "East Africa", "South Africa"],
    "South Africa": ["Congo", "East Africa", "Madagascar"],
    "Madagascar": ["East Africa", "South Africa"],
    "Western Europe": ["North Africa", "Southern Europe", "Northern Europe", "Great Britain"],
    "Southern Europe": ["Western Europe", "Northern Europe", "Ukraine", "Middle East", "Egypt", "North Africa"],
    "Northern Europe": ["Western Europe", "Southern Europe", "Ukraine", "Scandinavia", "Great Britain"],
    "Great Britain": ["Western Europe", "Northern Europe", "Scandinavia", "Iceland"],
    "Iceland": ["Greenland", "Great Britain", "Scandinavia"],
    "Scandinavia": ["Iceland", "Great Britain", "Northern Europe", "Ukraine"],
    "Ukraine": ["Northern Europe", "Southern Europe", "Ural", "Afghanistan", "Middle East", "Scandinavia"],
    "Afghanistan": ["Ukraine", "Ural", "China", "India", "Middle East"],
    "Ural": ["Ukraine", "Siberia", "China", "Afghanistan"],
    "Siberia": ["Ural", "Yakutsk", "Irkutsk", "Mongolia", "China"],
    "Yakutsk": ["Siberia", "Kamchatka", "Irkutsk"],
    "Kamchatka": ["Yakutsk", "Alaska", "Irkutsk", "Mongolia", "Japan"],
    "Irkutsk": ["Siberia", "Yakutsk", "Kamchatka", "Mongolia"],
    "Mongolia": ["Irkutsk", "Kamchatka", "Japan", "China", "Siberia"],
    "Japan": ["Kamchatka", "Mongolia"],
    "China": ["Mongolia", "Siberia", "Ural", "Afghanistan", "India", "Siam"],
    "India": ["Afghanistan", "China", "Middle East", "Siam"],
    "Siam": ["India", "China", "Indonesia"],
    "Indonesia": ["Siam", "New Guinea", "Western Australia"],
    "New Guinea": ["Indonesia", "Western Australia", "Eastern Australia"],
    "Western Australia": ["Indonesia", "New Guinea", "Eastern Australia"],
    "Eastern Australia": ["New Guinea", "Western Australia"],
    "Middle East": ["Southern Europe", "Egypt", "East Africa", "Afghanistan", "India", "Ukraine"]
}


CONTINENT_BONUSES = {
    "North America": (["Alaska", "Northwest Territory", "Greenland", "Alberta", "Ontario", "Quebec",
                       "Western United States", "Eastern United States", "Central America"], 5),
    "South America": (["Venezuela", "Peru", "Brazil", "Argentina"], 2),
    "Europe": (["Iceland", "Great Britain", "Scandinavia", "Ukraine", "Northern Europe", "Western Europe", "Southern Europe"], 5),
    "Africa": (["North Africa", "Egypt", "East Africa", "Congo", "South Africa", "Madagascar"], 3),
    "Asia": (["Ural", "Siberia", "Yakutsk", "Kamchatka", "Irkutsk", "Mongolia", "Japan", "Afghanistan", "China", "Middle East",
              "India", "Siam"], 7),
    "Australia": (["Indonesia", "New Guinea", "Western Australia", "Eastern Australia"], 2)
}