from pre_traitment import read_json, read_synonyms
import nltk
import re
import numpy

class Websearcher():
    def __init__(self):
        self.brand_index = read_json("TP3/input/brand_index.json")
        self.description_index = read_json("TP3/input/description_index.json")
        self.origin_index = read_json("TP3/input/origin_index.json")
        self.reviews_index = read_json("TP3/input/reviews_index.json")
        self.title_index = read_json("TP3/input/title_index.json")
        self.origin_synonyms = read_json("TP3/input/origin_synonyms.json")
        nltk.download('stopwords')
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
    
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
    
    def find_synonym(self, token):
        for values in self.origin_synonyms.values():
            if token in values:
                return next(key for key, value in self.origin_synonyms.items() if value == values)
        return None
    
    def replace_by_synonym(self, position, request_tokenized):
        synonym = self.find_synonym(request_tokenized[position])
        if synonym is None:
            return None
        request = request_tokenized.copy()
        request[position] = synonym
        return request

    
    def request_traitment(self, request):
        cleaned_tokens = self.tokenize_and_clean_text(request)
        request = cleaned_tokens
        for position in range(len(cleaned_tokens)):
            synonym_request = self.replace_by_synonym(position, request)
            if synonym_request is None:
                continue
            request = synonym_request
        return request
    
    def verify_at_least_one_token(self, tokens, index):
        all_urls = set()
        for token in tokens:
            if token in index.keys():
                if isinstance(index[token], dict):
                    all_urls |= set(index[token].keys())
                else:
                    all_urls |= set(index[token])
        return all_urls

        

    def verify_all_tokens(self, tokens, index):
        all_urls = None
        for token in tokens:
            if token in index.keys():
                if isinstance(index[token], dict):
                    if all_urls is None:
                        all_urls = set(index[token].keys())
                    else:
                        all_urls &= set(index[token].keys())
                else:
                    if all_urls is None:
                        all_urls = set(index[token])
                    else:
                        all_urls &= set(index[token])
            else:
                return set()
        return all_urls
    
    def filter_documents(self, tokens):
        all_in_title = self.verify_all_tokens(tokens, self.title_index)
        all_in_description = self.verify_all_tokens(tokens, self.description_index)
        at_least_one_in_title = self.verify_at_least_one_token(tokens, self.title_index)
        at_least_one_in_description = self.verify_at_least_one_token(tokens, self.description_index)
        at_least_one_in_brand= self.verify_at_least_one_token(tokens, self.brand_index)
        at_least_one_in_origin= self.verify_at_least_one_token(tokens, self.origin_index)
        return all_in_title, all_in_description, at_least_one_in_title, at_least_one_in_description, at_least_one_in_brand, at_least_one_in_origin

    def inverse_document_frequency(self, token, filtered_documents):
        number_of_documents = len(filtered_documents)
        documents_where_token_appeared = set()
        documents_where_token_appeared |= self.verify_at_least_one_token([token], self.title_index)
        documents_where_token_appeared |= self.verify_at_least_one_token([token], self.description_index)
        documents_where_token_appeared |= self.verify_at_least_one_token([token], self.brand_index)
        documents_where_token_appeared |= self.verify_at_least_one_token([token], self.origin_index)
        number_of_documents_where_token_appeared = len(documents_where_token_appeared)
        return numpy.log(number_of_documents/number_of_documents_where_token_appeared)
    
    def frequency_of_token_in_document(self, token, url):
        frequency = 0
        if url in self.title_index[token]:
            frequency += len(self.title_index[token][url])
        if url in self.description_index[token]:
            frequency += len(self.description_index[token][url])
        if url in self.origin_index[token]:
            frequency += 1
        if url in self.brand_index[token]:
            frequency += 1
        return frequency
    
    def mean_length_of_documents(self, filtered_documents):
        length_of_documents = []
        for document in filtered_documents:
            length = 0
            for token in self.title_index.keys():
                if document in token.keys():
                    length += len(token[document])
            for token in self.description_index.keys():
                if document in token.keys():
                    length += len(token[document])
            for token in self.origin_index:
                    if document in token:
                        length += 1
            for token in self.brand_index:
                    if document in token:
                        length +=1
            length_of_documents.append(length)
        return numpy.mean(length_of_documents), length_of_documents
    
    def len_penalization(self, length_document, mean):
        return length_document / mean
    
    def bm25(self, filtered_documents):
        mean_length_documents, length_of_documents = self.mean_length_documents(filtered_documents)
        for document in filtered_documents:
            pass
        



websearcher = Websearcher()
