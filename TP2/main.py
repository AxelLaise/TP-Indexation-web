from index import Index
import json

if __name__ == "__main__":
    index = Index("TP2/products.jsonl")
    title_index = index.create_title_index_with_position()
    description_index = index.create_description_index_with_position()
    reviews_index = index.create_reviews_index()
    brand_index = index.create_feature_index("brand")
    origin_index = index.create_feature_index("made in")
    flavor_index = index.create_feature_index("flavor")
    material_index = index.create_feature_index("material")
    with open('TP2/output/title_index.json', 'w') as file:
        json.dump(title_index, file, indent=1)
    with open('TP2/output/description_index.json', 'w') as file:
        json.dump(description_index, file, indent=1)
    with open('TP2/output/reviews_index.json', 'w') as file:
        json.dump(reviews_index, file, indent=1)
    with open('TP2/output/brand_index.json', 'w') as file:
        json.dump(brand_index, file, indent=1)
    with open('TP2/output/origin_index.json', 'w') as file:
        json.dump(origin_index, file, indent=1)
    with open('TP2/output/flavor_index.json', 'w') as file:
        json.dump(flavor_index, file, indent =1)
    with open('TP2/output/material_index.json', 'w') as file:
        json.dump(material_index, file, indent=1)