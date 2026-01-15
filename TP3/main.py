from websearcher import Websearcher

websearcher = Websearcher()
queries = [
    # Simple keywords
    "chocolate",
    "sneakers",
    
    # Exact match
    "chocolate candy",
    "energy drink",

    #variant search
    "blue drink pack",
    "cherry chocolate",
    
    # Origin / brand tests
    "france chocolate",
    "usa shoes",
    "timelessfootwear sneakers",

    # Impossible combination
    "timelessfootwear chocolate",
    "MagicSteps cat ear  beanie from india",
    
    # Very precise queries
    "Chocolate medium size from France",
    "children Sneakers for kids from dutch",
    
    # Query with no matching documents
    "space rocket"
]

for query in queries:
    search_result = websearcher.search(query)
    websearcher.save_search(search_result, query)
    