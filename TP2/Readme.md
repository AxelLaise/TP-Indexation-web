# TP2
## Index Structure
### Title Index

A positional inverted index built from the `title` field.
For each token, the index stores the url of the documents in which it appears and the corresponding positions.

**Structure:**

```json
{
  "token": {
    "document_url": [0, 4]
  }
}
```

### Description Index

A positional inverted index built from the `description` field.
For each token, the index stores the urls of the documents in which it appears and the corresponding positions.

```json
{
  "token": {
    "document_url": [0, 28]
  }
}
```


### Feature Indexes

An inverted index built from some features from the `product_features` field.

#### Selected Features

The following features were selected because they are:

* frequent in the dataset,
* relevant for search and filtering.

Selected features:

* `brand`
* `made in`
* `material`
* `flavor`

These features are enough to search a document in the index because there is a lot of repetition in the dataset.
For example each variant of a same product has the same product_features so more features will not help to select over variants.
Because or dataset is not very large `brand` and `made_in` may be enough to select over the dataset but material and flavor can be used to classify more easily document for a research. 

**Structure:**

```json
{
  "feature_value": ["document1_url", "document2_url"]
}
```


### Reviews Index

For each document, the index stores:

* total number of reviews,
* mean_mark (between 1 and 5),
* last rating.

**Structure:**

```json
{
  "document_url": {
    "total_reviews": 5,
    "mean_mark": 4.3,
    "last_rating": 5
  }
}
```
## Implementation Choices

* Url preprocessing is done by one function that combine others function that we can find in url_traitment.py.  
* An object-oriented approach was used for indexing. A single `Index` class use the path to the data as initialization parameter and store the data after preprocessing as attributes of the class.
* The tokenization and cleaning are done with one method of `Index` class which used other methods and stopwords from nltk.
* Because title and description are indexed the same way there is one method that take either one or the other as parameter to create the index. However for readability and simplicity there is one method for each of these field that call the common method.
* There is one method to index any feature with only it's name so it is easy to add a feature to index.
* There is a unique method to index the reviews because it is the only non inversed index.
* A method is used to store index in the `output` file.

## Example of usage
An example of index is written in the main.py file.
```python
    from index import Index
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
```

## How to Run

You can run the example by executing this in the root directory:

```bash
python TP2/main.py
```

