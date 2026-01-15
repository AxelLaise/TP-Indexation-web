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
    index.save_index(title_index, "title_index")
    index.save_index(description_index, "description_index")
    index.save_index(reviews_index, "reviews_index")
    index.save_index(brand_index, "brand_index")
    index.save_index(origin_index, "origin_index")
    index.save_index(flavor_index, "flavor_index")
    index.save_index(material_index, "material_index")