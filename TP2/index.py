from TP2.url_traitment import extract_from_all_line
import nltk
import re

class Index():
    def __init__(self, path):
        nltk.download('stopwords')
        nltk.download('punkt')
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
        self.data = extract_from_all_line(path)

    def tokenize(self, text):
        return text.lower().split()
    
    def remove_stopwords(self, tokens):
        for token in tokens:
            if token in self.stopwords:
                tokens.remove(token)
        return tokens
    
    def remove_punctuation(self,tokens):
        return [re.sub(r'[^\w\s]', '', token) for token in tokens if re.sub(r'[^\w\s]', '', token)]
                
    def tokenize_and_clean_text(self, text):
        tokens = self.tokenize(text)
        clean_tokens= self.remove_stopwords(tokens)
        clean_tokens = self.remove_punctuation(clean_tokens)
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


index = Index("TP2/products.jsonl")
title_index = index.create_title_index()
description_index = index.create_description_index()

