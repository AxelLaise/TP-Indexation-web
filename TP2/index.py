from TP2.url_traitment import extract_from_all_line
import re
import nltk

class Index():
    def __init__(self, path):
        nltk.download('stopwords')
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
        self.data = extract_from_all_line(path)

    def tokenize(self, text):
        return text.lower().split()
    
    def remove_stopwords(self, tokens):
        return [token for token in tokens if not token in self.stopwords ]
    
    def remove_punctuation(self,tokens):
        return [re.sub(r'[^\w\s]', '', token) for token in tokens if re.sub(r'[^\w\s]', '', token)]
                
    def tokenize_and_clean_text(self, text):
        tokens = self.tokenize(text)
        clean_tokens = self.remove_punctuation(tokens)
        clean_tokens= self.remove_stopwords(clean_tokens)
        return clean_tokens
    
    def create_title_index(self):
        title_index = {}
        for line in self.data:
            title = line["title"]
            cleaned_title = self.tokenize_and_clean_text(title)
            for token in cleaned_title:
                if token in title_index.keys():
                    title_index[f"{token}"].append(line["url"])
                else:
                    title_index[f"{token}"] = [line["url"]]
        return title_index
    
    def create_description_index(self):
        description_index = {}
        for line in self.data:
            description = line["description"]
            cleaned_description = self.tokenize_and_clean_text(description)
            for token in cleaned_description:
                if token in description_index.keys():
                    description_index[f"{token}"].append(line["url"])
                else:
                    description_index[f"{token}"] = [line["url"]]
        return description_index

    def get_token_position(self, tokens, token):
        return [position for position, value in enumerate(tokens) if value == token]
    
    def create_title_index_with_position(self):
        title_index = {}
        for line in self.data:
            title = line["title"]
            cleaned_title = self.tokenize_and_clean_text(title)
            for token in cleaned_title:
                positions = self.get_token_position(cleaned_title, token)
                if not token in title_index.keys():
                    title_index[f"{token}"] = {}
                if not line["url"] in title_index[f"{token}"].keys():  #pas de doublon
                    title_index[f"{token}"][line["url"]] = positions
        return title_index
    
    def create_description_index_with_position(self):
        description_index = {}
        for line in self.data:
            description = line["description"]
            cleaned_description = self.tokenize_and_clean_text(description)
            for token in cleaned_description:
                positions = self.get_token_position(cleaned_description, token)
                if not token in description_index.keys():
                    description_index[f"{token}"] = {}
                if not line["url"] in description_index[f"{token}"].keys():  #pas de doublon
                    description_index[f"{token}"][line["url"]] = positions
        return description_index
    
    def extract_reviews_info(self, line):
        product_reviews = line["product_reviews"]
        if product_reviews != []:
            number_of_rating = len(product_reviews)
            product_reviews = sorted(product_reviews, key=lambda x: x["date"], reverse=True)
            last_rating = product_reviews[0]["rating"]
            avg_rating = 0
            for review in product_reviews:
                avg_rating += int(review["rating"])
            avg_rating = avg_rating/number_of_rating
        else:
            number_of_rating = 0
            last_rating = 0
            avg_rating = 0
        return number_of_rating, last_rating, avg_rating

    def create_reviews_index(self):
        reviews_index = {}
        for line in self.data:
            number_of_rating, last_rating, avg_rating = self.extract_reviews_info(line)
            reviews_index[line["url"]] = {"total_reviews": number_of_rating, "mean_mark": avg_rating, "last_rating": last_rating}
        return reviews_index

    def create_feature_index(self, feature):
        feature_index = {}
        for line in self.data:
            if feature in line["product_features"].keys():
                feature_text = line["product_features"][feature]
                cleaned_featured = self.tokenize_and_clean_text(feature_text)
                for token in cleaned_featured:
                    if token in feature_index.keys():
                        feature_index[f"{token}"].append(line["url"])
                    else:
                        feature_index[f"{token}"] = [line["url"]]
        return feature_index