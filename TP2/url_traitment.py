import urllib.parse
import json

def read_jsonl(path):
    data=[]
    with open(path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data

def extract_id_produit(url_parse):
    path = url_parse.path
    if path.startswith("/product/"):
        id_produit = path[9:]
        if id_produit != '':
            return id_produit
    return None

def extract_variant(url_parse):
    path = url_parse.path
    query = url_parse.query
    if path.startswith("/product/") and query != '':
        variant = query[8:]
        return variant
    return None

def extract_from_one_line(line):
    url = line["url"]
    url_parse = urllib.parse.urlparse(url)
    id_produit = extract_id_produit(url_parse)
    variant = extract_variant(url_parse)
    if id_produit is not None:
        line["id_produit"] = id_produit
    if variant is not None:
        line["variant"] = variant
    return line

def extract_from_all_line(path):
    data = read_jsonl("TP2/products.jsonl")
    for line in data:
        line = extract_from_one_line(line)
    return data
