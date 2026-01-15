from TP2.url_traitment import extract_from_all_page
import re
import nltk
import json

class Index():
    def __init__(self, path):
        nltk.download('stopwords')
        self.stopwords = set(nltk.corpus.stopwords.words('english')) # A list of words classify as stopwords by nltk
        self.data = extract_from_all_page(path)

    def tokenize(self, text):
        """
        Parameter
        ---------
        text: String
            The original text to tokenize
        
        Return
        ------
        List[String]
            the tokenized version of the text
        """
        return text.lower().split()
    
    def remove_stopwords(self, tokens):
        """
        Parameter
        ---------
        tokens: List[String]
            A tokenized version of a text without punctuation
        
        Return
        ------
        List[String]
            The tokenized version of a text without stopwords
        """
        return [token for token in tokens if not token in self.stopwords ]
    
    def remove_punctuation(self,tokens):
        """
        Parameter
        ---------
        tokens: List[String]
            A tokenized version of a text
        
        Return
        ------
        List[String]
            The tokenized version of a text without punctuation
        """
        return [re.sub(r'[^\w\s]', '', token) for token in tokens if re.sub(r'[^\w\s]', '', token)]
                
    def tokenize_and_clean_text(self, text):
        """
        Parameter
        ---------
        text: String
            The original text to tokenize
        
        Return
        ------
        List[String]
            the tokenized version of the text without punctuation and stopwords
        """
        tokens = self.tokenize(text)
        clean_tokens = self.remove_punctuation(tokens)
        clean_tokens= self.remove_stopwords(clean_tokens)
        return clean_tokens
    
    def create_title_index(self):
        """
        Return
        ------
        Dict
            The inverted index of the title for the database
        """
        title_index = {}
        for page in self.data:
            title = page["title"]
            cleaned_title = self.tokenize_and_clean_text(title)
            for token in cleaned_title:
                if token in title_index.keys():
                    title_index[token].append(page["url"])
                else:
                    title_index[token] = [page["url"]]
        return title_index
    
    def create_description_index(self):
        """
        Return
        ------
        Dict
            The inverted index of the description for the database
        """
        description_index = {}
        for page in self.data:
            description = page["description"]
            cleaned_description = self.tokenize_and_clean_text(description)
            for token in cleaned_description:
                if token in description_index.keys():
                    description_index[token].append(page["url"])
                else:
                    description_index[token] = [page["url"]]
        return description_index

    def get_token_position(self, tokens, token):
        """
        Parameter
        ---------
        tokens: List[String]
            the tokenized version of the text
        token: String
            a token
        
        Return
        ------
        List[int]
            The positions of the given token in the tokenized text.
        """
        return [position for position, value in enumerate(tokens) if value == token]
    
    def create_title_index_with_position(self):
        """
        Return
        ------
        Dict
            The inverted index of the title for the database with positions in each documents
        """
        title_index = {}
        for page in self.data:
            title = page["title"]
            cleaned_title = self.tokenize_and_clean_text(title)
            for token in cleaned_title:
                positions = self.get_token_position(cleaned_title, token)
                if not token in title_index.keys():
                    title_index[token] = {}
                if not page["url"] in title_index[token].keys(): # To avoid doing twice the same word in the same page
                    title_index[token][page["url"]] = positions
        return title_index
    
    def create_description_index_with_position(self):
        """
        Return
        ------
        Dict
            The inverted index of the description for the database with positions in each documents
        """
        description_index = {}
        for page in self.data:
            description = page["description"]
            cleaned_description = self.tokenize_and_clean_text(description)
            for token in cleaned_description:
                positions = self.get_token_position(cleaned_description, token)
                if not token in description_index.keys():
                    description_index[token] = {}
                if not page["url"] in description_index[token].keys(): # To avoid doing twice the same word in the same page
                    description_index[token][page["url"]] = positions
        return description_index
    
    def extract_reviews_info(self, page):
        """
        Extract from one page the number of ratings, last rating and average rating

        Parameter
        ---------
        page: Dict
            Informations of the page

        Return
        ------
        Tuple
            the number of ratings, last rating and average rating of the given page
        """
        product_reviews = page["product_reviews"]
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
        """
        Return
        ------
        Dict
            Informations about reviews for each document
        """
        reviews_index = {}
        for page in self.data:
            number_of_rating, last_rating, avg_rating = self.extract_reviews_info(page)
            reviews_index[page["url"]] = {"total_reviews": number_of_rating, "mean_mark": avg_rating, "last_rating": last_rating}
        return reviews_index

    def create_feature_index(self, feature):
        """
        Parameter
        ---------
        feature: String
            The name of the feature we want to index

        Return
        ------
        Dict
            The inverted index of the feature for the database
        """
        feature_index = {}
        for page in self.data:
            if feature in page["product_features"].keys():
                feature_text = page["product_features"][feature]
                cleaned_featured = self.tokenize_and_clean_text(feature_text)
                for token in cleaned_featured:
                    if token in feature_index.keys():
                        feature_index[token].append(page["url"])
                    else:
                        feature_index[token] = [page["url"]]
        return feature_index
    
    def save_index(self, index, file_name):
        """
        Parameter
        ---------
        index: Dict
            The index or inverted index to save in a json file
        
        file_name: String
            The name of the json file to write the index
        """
        with open(f'TP2/output/{file_name}.json', 'w') as file:
            json.dump(index, file, indent=1)