
import pandas as pd
from elasticsearch import Elasticsearch, helpers
import json


def normalise_min_max(df):
    '''
    df all cols should be numerical 
    note: normalising values between 1 to 2
    '''
    df = pd.DataFrame()
    for column in df.columns:
        df[column+"_norm"] = ((df[column] - df[column].min()) /
                              (df[column].max() - df[column].min())+1)
    return df


def get_null_count(filename):
    df = pd.read_csv(filename)
    return df.isnull().sum()


def connect_elastic():
    client = Elasticsearch("http://localhost:9200")
    if client.ping():
        print("yay.. connected ")

    else:
        print("Cannot connect.")
    return client


def get_default_vector():
    try:
        with open('default_vector_values.txt', 'r') as file:
            data = file.read()
        data = data.split('|')
        data = [float(i) for i in data]
        return data
    except Exception as e:
        print('Error while reading default vectors')
        print(e)
        return []


def update_user_vector(prev_vec, change_dict):
    """
    change_dict - {
        index - list,
        value - list
    }
    """
    # [1,4,7]

    for i, ind in enumerate(change_dict["index"]):
        prev_vec[ind] = change_dict["value"][i]
    return prev_vec


#### for single instance of db connections through out whole program
class es_instance:
    __singleton_instance = None
    # define the classmethod

    @classmethod
    def get_instance(cls):
        # check for the singleton instance
        if not cls.__singleton_instance:
            cls.__singleton_instance = connect_elastic()

        # return the singleton instance
        return cls.__singleton_instance


def cosine_in_elastic_search(index_name: str, query_vector: list, no_of_values: int):
    '''
        args: 
            index_name: database name or index name in es tems
            query_vector: users vector 
            no_of_values: how many recommendations he want

        returns: 
            responses: es object with cosine similarity matches of 
    '''

    es = es_instance.get_instance()
    search_query = {
        "size": no_of_values,
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": "cosineSimilarity(params.queryVector, 'vector') + 1.0",
                    "params": {
                        "queryVector": query_vector
                    }
                }
            }
        }
    }
    responses = es.search(index=index_name, body=search_query)
    similarities = []
    for data in responses['hits']['hits']:
        response_to_be_shown = {
            "brand": data['_source']['brand'],
            "series": data['_source']['series'],
            "price": data['_source']['price'],
            "url": data['_source']['url'],
            'rating': float(data['_source']['rating'][:3]),
            "image_url": data['_source']['image_url'],
            "display": data['_source']["display"]
        }
        similarities.append(response_to_be_shown)
    return similarities


def update_vector(arr, indexes, values):
    ## to keep the default values same when user have no specifications
    if not values:
        return arr
    for i in range(len(indexes)):
        arr[indexes[i]] = values[i]
    return arr

