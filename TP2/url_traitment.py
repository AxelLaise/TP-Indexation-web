import urllib.parse
import json

def read_jsonl(path):
    """
    Parameter
    ---------
    path: String
        The path of the jsonl

    Return
    ------
    List(Dict)
        A list containing each page of the jsonl
    """
    data=[]
    with open(path, "r") as f:
        for page in f:
            data.append(json.loads(page))
    return data

def extract_id_produit(url_parse):
    """
    Extract from the url the id of the product if it exists

    Parameter
    ---------
    url_parse: urlparse
        The parsing of the url by urllib
    """
    path = url_parse.path
    if path.startswith("/product/"):
        id_produit = path[9:]
        if id_produit != '':
            return id_produit
    return None

def extract_variant(url_parse):
    """
    Extract from the url the variant of the product if it exists

    Parameter
    ---------
    url_parse: urlparse
        The parsing of the url by urllib
    """
    path = url_parse.path
    query = url_parse.query
    if path.startswith("/product/") and query != '':
        variant = query[8:]
        return variant
    return None

def extract_from_one_page(page):
    """
    Extract from one page the id and the variant of the product if they exist

    Parameter
    ---------
    page: Dict
        Informations of the page

    Return
    ------
    Dict
        Informations of the page with product_id and variant as new keys
    """
    url = page["url"]
    url_parse = urllib.parse.urlparse(url)
    id_produit = extract_id_produit(url_parse)
    variant = extract_variant(url_parse)
    if id_produit is not None:
        page["id_produit"] = id_produit
    if variant is not None:
        page["variant"] = variant
    return page

def extract_from_all_page(path):
    """
    Add product_id and variant if they exist to all pages as new keys

    Parameter
    ---------
    path: String
        The path of the jsonl

    Return
    ------
    List[Dict]
        List of informations about pages with product_id and variant as new keys for each page
    """
    data = read_jsonl("TP2/products.jsonl")
    for page in data:
        page = extract_from_one_page(page)
    return data
