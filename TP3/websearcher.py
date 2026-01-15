from pre_traitment import read_json, read_jsonl
import nltk
import re
import numpy
import json

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
        self.data = read_jsonl("TP3/rearranged_products.jsonl")
    
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
        """
        Parameter
        ---------
        token: String
        
        Return
        ------
        String
            the synonym  of the token from the dictionnary if it exists 
        """
        for values in self.synonyms.values():
            if token in values:
                return next(key for key, value in self.synonyms.items() if value == values)
        return None
    
    def replace_by_synonym(self, position, query_tokenized):
        """
        Parameter
        ---------
        position: int
            the position of the token to replace

        query_tokenized: String
        
        Return
        ------
        List[String]
            The query with the token replaced by it's synonym
        """
        synonym = self.find_synonym(query_tokenized[position])
        if synonym is None:
            return None
        query = query_tokenized.copy()
        query[position] = synonym
        return query

    
    def query_traitment(self, query):
        """
        Parameter
        ---------
        query: String
        
        Return
        ------
        List[String]
            the query after processing (tokenization, synonyms, remove_stopwords)
        """
        cleaned_tokens = self.tokenize_and_clean_text(query)
        query = cleaned_tokens
        for position in range(len(cleaned_tokens)):
            synonym_query = self.replace_by_synonym(position, query)
            if synonym_query is None:
                continue
            query = synonym_query
        return query
    
    def verify_at_least_one_token(self, tokens, index):
        """
        Parameter
        ---------
        tokens: List[String]
        
        index: Dict
            the index where we want to search
        Return
        ------
        set(String)
            all documents where a token appeared at least once in the chosen index
        """
        all_documents = set()
        for token in tokens:
            if token in index.keys():
                if isinstance(index[token], dict):
                    all_documents |= set(index[token].keys())
                else:
                    all_documents |= set(index[token])
        return all_documents

        

    def verify_all_tokens(self, tokens, index):
        """
        Parameter
        ---------
        tokens: List[String]
        
        index: Dict
            the index where we want to search
        Return
        ------
        set(String)
            all documents where every tokens appeared in the chosen index
        """
        all_documents = None
        for token in tokens:
            if token in index.keys():
                if isinstance(index[token], dict):
                    if all_documents is None:
                        all_documents = set(index[token].keys())
                    else:
                        all_documents &= set(index[token].keys())
                else:
                    if all_documents is None:
                        all_documents = set(index[token])
                    else:
                        all_documents &= set(index[token])
            else:
                return set()
        return all_documents
    
    def filter_documents(self, tokens):
        """
        Parameter
        ---------
        tokens: List[String]
        
        Return
        ------
        set(String)
            all documents where a token appeared at least once
        """
        filtered_documents = self.verify_at_least_one_token(tokens, self.title_index)
        filtered_documents |= self.verify_at_least_one_token(tokens, self.description_index)
        filtered_documents |= self.verify_at_least_one_token(tokens, self.brand_index)
        filtered_documents |= self.verify_at_least_one_token(tokens, self.origin_index)
        return filtered_documents

    def inverse_document_frequency(self, token, filtered_documents, index):
        """
        Parameter
        ---------
        token: String

        filtered_documents: set(String)

        index: Dict
            Corresponding to the field in the definition of the lesson
        
        Return
        ------
        float
            The value of the IDF for the given token and the given field
        """
        number_of_documents = len(filtered_documents)
        documents_where_token_appeared = set()
        documents_where_token_appeared |= self.verify_at_least_one_token([token], index) # Find all document where the token appeared in the given index
        number_of_documents_where_token_appeared = len(documents_where_token_appeared)
        return numpy.log((number_of_documents + 1)/(number_of_documents_where_token_appeared + 1)) # The +1 to avoid dividing by 0 and doing log(0)
    
    def frequency_of_token_in_document(self, token, document, index):
        """
        Parameter
        ---------
        token: String

        document: String
            the url of a document

        index: Dict
            Corresponding to the field in the definition of the lesson
        
        Return
        ------
        Integer
            The value of the frequency for the given token in the given document and the given field
        """
        frequency = 0
        if token in index.keys():
            if document in index[token].keys():
                frequency += len(index[token][document])
        return frequency
    
    def mean_length_of_documents(self, filtered_documents, index):
        """
        Parameter
        ---------
        filtered_documents: set(String)

        index: Dict
            Corresponding to the field in the definition of the lesson
        
        Return
        ------
        float
            The average length of documents from the filtered documents for the given field
        
        List[Integer]
            The length of the documents in the filtered document set for the given field
        """
        length_of_documents = []
        for document in filtered_documents:
            length = 0
            for token in index.keys():
                if document in index[token].keys():
                    length += len(index[token][document])
            length_of_documents.append(length)
        return numpy.mean(length_of_documents), length_of_documents
    
    def len_penalization(self, length_document, mean):
        """
        Parameter
        ---------
        length_document: Integer
            The length of a document 

        mean: float
            The average length of documents from the filtered documents
        
        Return
        ------
        float
            The value of the penalization in bm25 formula
        """
        return length_document / mean
    
    def bm25(self, filtered_documents, tokens, index, b=0.75, k1=1.2):
        """
        Parameter
        ---------
        filtered_documents: set(String)

        tokens: List[String]

        index: Dict
            Corresponding to the field in the definition of the lesson
        
        Return
        ------
        float
            The bm25 score for the given corpus, query and field
        """
        mean_length_documents, length_of_documents = self.mean_length_of_documents(filtered_documents, index)
        bm25_score = {}
        for i, document in enumerate(filtered_documents):
            bm25 = 0
            for token in tokens:
                frequency = self.frequency_of_token_in_document(token, document, index)
                if frequency == 0:
                    continue # To avoid dividing by 0 
                             # in this case the term in the sum is equal to 0 so we don't need to calculate everything else for this token
                IDF = self.inverse_document_frequency(token, filtered_documents, index)
                len_pen = self.len_penalization(length_of_documents[i], mean_length_documents)
                score_for_token = IDF * (frequency * (k1 + 1))/(frequency + k1 * (1-b + b *len_pen))
                bm25 += score_for_token
            bm25_score[document] = bm25
        return bm25_score
    
    def exact_match(self, tokens, document, index):
        """
        Parameter
        ---------
        tokens: List[String]

        document: String
            the url of the document

        index: Dict
        
        Return
        ------
        Integer
            1 if there is an exact match in the given index 0 otherwise
        """
        if len(tokens) < 2: #There is no exact match for a one word query
            return 0

        positions = []
        for token in tokens:
            if token in index:
                if document in index[token]: # verify if all tokens are in the document
                    positions.append(index[token][document]) 
            else:
                return 0

        for pos in positions[0]:
            if all((pos + i) in positions[i] for i in range(len(tokens))): # An exact match is defined by all the tokens in the same order next to each others
                return 1
        return 0
    
    def early_match(self, tokens, document, index):
        """
        Parameter
        ---------
        tokens: List[String]

        document: String
            the url of the document

        index: Dict
        
        Return
        ------
        float
            between 0 and 1 to represent if the first token to match the query and the document is early in the document
        """
        positions = []
        for token in tokens:
            if token in index:
                if document in index[token]:
                    positions.append(min(index[token][document]))
        return 1 / (1 + min(positions)) if positions else 0 # It only depends on the first token of the document in the given index.

    
    def linear_scoring(self, tokens, filtered_documents):
        """
        Parameter
        ---------
        tokens: List[String]

        filtered_documents
        
        Return
        ------
       List[List[float, String]]
            The ranking of every filtered documents
        """
        # The description of different scoring methods and ponderation are in the analysis.md file
        bm25_title = self.bm25(filtered_documents, tokens, self.title_index)
        bm25_desc  = self.bm25(filtered_documents, tokens, self.description_index)
            
        rank = []
        docs_all_title = self.verify_all_tokens(tokens, self.title_index)
        docs_all_desc  = self.verify_all_tokens(tokens, self.description_index)
        docs_brand = self.verify_at_least_one_token(tokens, self.brand_index)
        docs_origin = self.verify_at_least_one_token(tokens, self.origin_index)

        for doc in filtered_documents:

            score_title = bm25_title.get(doc, 0) * 2
            score_desc  = bm25_desc.get(doc, 0)
            score = score_title + score_desc

            exact_title = self.exact_match(tokens, doc, self.title_index) * 5
            exact_desc  = self.exact_match(tokens, doc, self.description_index) 
            score += exact_title + exact_desc

            if doc in docs_all_title: score += 3
            if doc in docs_all_desc:  score += 0.5
            if doc in docs_brand: score += 1
            if doc in docs_origin: score += 1

            review = self.reviews_index[doc]
            review_score = numpy.log(1 + review["total_reviews"]) * review["mean_mark"] * 0.2
            score += review_score

            early_desc  = self.early_match(tokens, doc, self.description_index)
            score += early_desc

            rank.append(score)
            #This was used to adjust weight on different signals

            #score_for_one_doc["all_tokens_in_title"] = 0
            #score_for_one_doc["all_tokens_in_desc"] = 0
            #score_for_one_doc["token_in_brand"] = 0
            #score_for_one_doc["token_in_origin"] = 0
            #score_for_one_doc["bm25_title"] = score_title
            #score_for_one_doc["bm25_description"] = score_desc
            #score_for_one_doc["exact_title"] = exact_title
            #score_for_one_doc["exact_description"] = exact_desc
            #if doc in docs_all_title: score_for_one_doc["all_tokens_in_title"] = 3
            #if doc in docs_all_desc: score_for_one_doc["all_tokens_in_desc"] = 0.5
            #if doc in docs_brand: score_for_one_doc["token_in_brand"] = 2
            #if doc in docs_origin: score_for_one_doc["token_in_origin"] = 2
            #score_for_one_doc["review_score"] = review_score
            #score_for_one_doc["early_desc"] = early_desc
            #every_score.append(score_for_one_doc)

        final_score = [[rank[i], doc]for i, doc in enumerate(filtered_documents)]

        return final_score
    
    def extract_title_and_description(self, document):
        """
        Parameter
        ---------
        document: String
            the url of the document
        
        Return
        ------
        String
            The title of the given document
        String
            The description of the given document
        """
        title = self.data[document]["title"]
        description = self.data[document]["description"]
        return title, description

        
    def search(self, query):
        """
        Parameter
        ---------
        query: String

        Return
        ------
        Dict{Dict, Dict}
            The search result in order of ranking and the metadata of the query (number of filtered documents and number of document in the dataset)
        """
        metadata = {}
        tokenized_query = self.query_traitment(query)
        filtered_documents = self.filter_documents(tokenized_query)
        score = self.linear_scoring(tokenized_query, filtered_documents)
        metadata["number_of_filtered_documents"] = len(filtered_documents)
        metadata["number_of_documents"] = len(self.data)
        score.sort(reverse=True)
        search_result = {}
        for rank, doc in score:
            title, description = self.extract_title_and_description(doc)
            search_result[doc]={}
            search_result[doc]["rank"] = rank
            search_result[doc]["title"] = title
            search_result[doc]["description"] = description
        return {"search_result": search_result, "metadata": metadata}
    
    def save_search(self, search_result, file_name):
        """
        Parameter
        ---------
        search_result: Dict
            The result of the search
        
        file_name: String
            The name of the json file to write the search result
        """
        with open(f'TP3/output/{file_name}.json', 'w') as file:
            json.dump(search_result, file, indent=1)
