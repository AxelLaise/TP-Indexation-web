## Documents filtering
To filter which documents to rank we only see if one token of the query is in the document title or in the description or if the brand or the origin exist. It is used because if a search is made about product made in India but this product do not exist in our database it will propose other products from India (same idea for the brand).

## Signals Used for Ranking

The final score of each document is computed using a linear combination of multiple signals:
* bm25 score on the title
* bm25 score on the description
* Exact match between the query and the title
* Exact match between the query and the description
* Presence of all query tokens in the title
* Presence of all query tokens in the description
* Presence of query tokens in the brand
* Presence of query tokens in the product origin
* Review-based score
* Early occurrence of query tokens in the description. We only take for the description because the title is short and it will always be in early position

We did not use the signal if at least one token appeared in a specific field because it is already used for filtering documents so it will be redundant with bm25 and filtering.

## Weighting Choices
The weights have been choosen after analysed the results of the queries from the main.py.

* BM25 score on the title x2
    Because the title is important to determine priority

* BM25 score on the description
    Less important than the title and it's raw value alone has enough impact

* Exact match title = 5
    If there is an exact match it boosts the document to the top with this value

* Exact match description = 2
    It is less important than title but it boosts the document

* All tokens in title = 3
    Less important than exact match but more than exact match for description

* All tokens in description = 1
    Can appeared a lot of time depending on the query so with this value it will not boosts too much documents

* Token in brand = 1

* Token in origin = 1
    For brand and origin it is only a secondary signal that are less important than products related signals
    For example if we search for a product and a brand but the brand do not sell this product (e.g "Nike chocolate") the searcher will give a better rank to document mentioning "chocolate" than document mentioning "nike"

* Reviews score * 0.2
    It is only used to make a little gap between very similar documents, the reviews score is really high that is why it is multiplied by 0.2

* Early occurrence in description × 0.8
    It is also used to distinguish very similar documents, the raw score is at most 1

## Analysis of results

### Filtered documents
For good queries (i.e with word that appeared at least in the corpus) the filtering select between 20 and 50 documents over the 150 documents of the corpus for the examples queries in main.py

### One word query
The bm25 is not a really good indicator for one word query because as filtered document are all document containing this word the IDF is equal to 0 and so the bm25. That is why in the results we can see that for one word query the first documents have the same ranking. In this case the ranking is really dependant of early description and reviews score because exact score is equal to  for one word queries.

### Exact query
The same problem is found for exact query, but that is why there is exact title and exact description score to help to distinguish in these cases.4

### Brand or origin query
The score will put first documents corresponding to products and brand/origin then only corresponding to product and then to the brand/origin.

### Impossible combination
As before it puts products and then brand/origin

### Precise queries
It will boost the document that correspond to the queries above others document

### Query with no matching documents
It has no document after filtering so no result for the search

## Limitations

* The title may be too much powerful to determine the ranking
* The synonyms gestion is not really good because of the gestion of tokens, it works here on this because we know how are redacted each documents. For example the united states synonym do not work with how i implement token because it represents two tokens in the implementation
* Also query are replaced by synonyms instead of searching the original query and the query with synonyms
* A proximity score could have been add to improve performance






