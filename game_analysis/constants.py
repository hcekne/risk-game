# Define the continent mapping (same as the CONTINENT_BONUSES without the bonuses)
continent_mapping = {
    "North America": ["Alaska", "Northwest Territory", "Greenland", "Alberta", "Ontario", "Quebec",
                      "Western United States", "Eastern United States", "Central America"],
    "South America": ["Venezuela", "Peru", "Brazil", "Argentina"],
    "Europe": ["Iceland", "Great Britain", "Scandinavia", "Ukraine", "Northern Europe", 
               "Western Europe", "Southern Europe"],
    "Africa": ["North Africa", "Egypt", "East Africa", "Congo", "South Africa", "Madagascar"],
    "Asia": ["Ural", "Siberia", "Yakutsk", "Kamchatka", "Irkutsk", "Mongolia", "Japan", "Afghanistan", 
             "China", "Middle East", "India", "Siam"],
    "Australia": ["Indonesia", "New Guinea", "Western Australia", "Eastern Australia"]
}

TERRITORIES_ORDERED_BY_CONTINENTS = [
    # North America
    "Alaska", "Northwest Territory", "Greenland", "Alberta", "Ontario", "Quebec",
    "Western United States", "Eastern United States", "Central America",
    
    # South America
    "Venezuela", "Peru", "Brazil", "Argentina",
    
    # Europe
    "Iceland", "Great Britain", "Scandinavia", "Ukraine", "Northern Europe",
    "Western Europe", "Southern Europe",
    
    # Africa
    "North Africa", "Egypt", "East Africa", "Congo", "South Africa", "Madagascar",
    
    # Asia
    "Ural", "Siberia", "Yakutsk", "Kamchatka", "Irkutsk", "Mongolia", "Japan",
    "Afghanistan", "China", "Middle East", "India", "Siam",
    
    # Australia
    "Indonesia", "New Guinea", "Western Australia", "Eastern Australia"
]