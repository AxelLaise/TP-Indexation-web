from pre_traitment import read_json
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
        self.synonyms = read_json("TP3/input/synonyms.json")
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
        for values in self.synonyms.values():
            if token in values:
                return next(key for key, value in self.synonyms.items() if value == values)
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
        filtered_documents = self.verify_at_least_one_token(tokens, self.title_index)
        filtered_documents |= self.verify_at_least_one_token(tokens, self.description_index)
        filtered_documents |= self.verify_at_least_one_token(tokens, self.brand_index)
        filtered_documents |= self.verify_at_least_one_token(tokens, self.origin_index)
        return filtered_documents

    def inverse_document_frequency(self, token, filtered_documents, index):
        number_of_documents = len(filtered_documents)
        documents_where_token_appeared = set()
        documents_where_token_appeared |= self.verify_at_least_one_token([token], index)
        number_of_documents_where_token_appeared = len(documents_where_token_appeared)
        return numpy.log((number_of_documents + 1)/(number_of_documents_where_token_appeared + 1))
    
    def frequency_of_token_in_document(self, token, url, index):
        frequency = 0
        if token in index.keys():
            if url in index[token].keys():
                frequency += len(index[token][url])
        return frequency
    
    def mean_length_of_documents(self, filtered_documents, index):
        length_of_documents = []
        for document in filtered_documents:
            length = 0
            for token in index.keys():
                if document in index[token].keys():
                    length += len(index[token][document])
            length_of_documents.append(length)
        return numpy.mean(length_of_documents), length_of_documents
    
    def len_penalization(self, length_document, mean):
        return length_document / mean
    
    def bm25(self, filtered_documents, tokens, index, b=0.75, k1=1.2):
        mean_length_documents, length_of_documents = self.mean_length_of_documents(filtered_documents, index)
        bm25_score = {}
        for i, document in enumerate(filtered_documents):
            bm25 = 0
            for token in tokens:
                frequency = self.frequency_of_token_in_document(token, document, index)
                if frequency == 0:
                    continue
                IDF = self.inverse_document_frequency(token, filtered_documents, index)
                len_pen = self.len_penalization(length_of_documents[i], mean_length_documents)
                score_for_token = IDF * (frequency * (k1 + 1))/(frequency + k1 * (1-b + b *len_pen))
                bm25 += score_for_token
            bm25_score[document] = bm25
        return bm25_score
    
    def exact_match(self, tokens, document, index):
        if len(tokens) < 2:
            return 0

        positions = []
        for token in tokens:
            if token in index and document in index[token]:
                positions.append(index[token][document])
            else:
                return 0

        for pos in positions[0]:
            if all((pos + i) in positions[i] for i in range(len(tokens))):
                return 1
        return 0
    
    def early_match(self, tokens, document, index):
        positions = []
        for token in tokens:
            if token in index:
                if document in index[token]:
                    positions.append(min(index[token][document]))
        return 1 / (1 + min(positions)) if positions else 0

    
    def linear_scoring(self, tokens, filtered_documents):
        bm25_title = self.bm25(filtered_documents, tokens, self.title_index)
        bm25_desc  = self.bm25(filtered_documents, tokens, self.description_index)
            
        midway_score = []
        docs_all_title = self.verify_all_tokens(tokens, self.title_index)
        docs_all_desc  = self.verify_all_tokens(tokens, self.description_index)
        docs_brand = self.verify_at_least_one_token(tokens, self.brand_index)
        docs_origin = self.verify_at_least_one_token(tokens, self.origin_index)

        for doc in filtered_documents:
            score_title = bm25_title.get(doc, 0)
            score_desc  = bm25_desc.get(doc, 0)
            score = score_title * 2 + score_desc

            exact_title = self.exact_match(tokens, doc, self.title_index)
            exact_desc  = self.exact_match(tokens, doc, self.description_index)
            score += exact_title * 5 + exact_desc * 2

            if doc in docs_all_title: score += 3
            if doc in docs_all_desc:  score += 1
            if doc in docs_brand: score += 2
            if doc in docs_origin: score += 2

            review = self.reviews_index[doc]
            review_score = numpy.log(1 + review["total_reviews"]) * review["mean_mark"]
            score += review_score

            early_title = self.early_match(tokens, doc, self.title_index)
            early_desc  = self.early_match(tokens, doc, self.description_index)
            score += 0.8 * (early_title * 2 + early_desc)

            midway_score.append(score)

        final_score = [
            [midway_score[i], doc]
            for i, doc in enumerate(filtered_documents)
        ]

        return final_score

    def search(self, request, limit=10):
        tokenized_request = self.request_traitment(request)
        print(tokenized_request)
        filtered_documents = self.filter_documents(tokenized_request)
        score = self.linear_scoring(tokenized_request, filtered_documents)
        score.sort(reverse=True)
        if limit > len(score):
            limit = len(score)
        res = [doc for _, doc in score[:limit]]
        return res




        

            
        



websearcher = Websearcher()
print(websearcher.search("drink energy"))