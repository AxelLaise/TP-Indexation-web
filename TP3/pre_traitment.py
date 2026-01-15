import json


def read_json(path):
    """
    Parameter
    ---------
    path: String
        The path of the jsonl

    Return
    ------
    List(Dict)
        A list containing each page of the json
    """
    with open(path, "r") as file:
        return json.load(file)

def read_jsonl(path):
    """
    Parameter
    ---------
    path: String
        The path of the jsonl

    Return
    ------
    Dict
        A dict containing each document dict with key equals to the url of the document
    """
    data={}
    with open(path, "r") as file:
        for page in file:
            document = (json.loads(page))
            data[document["url"]] = document
    return data
