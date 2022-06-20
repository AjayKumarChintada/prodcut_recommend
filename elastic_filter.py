from elasticsearch import helpers
import pandas as pd
from elasticsearch import Elasticsearch


df = pd.read_csv('laptop_data.csv')
df.drop(columns=['Graphic flag', 'product url'], inplace=True)
df.columns = ['brand', 'series', 'weight', 'ram', 'price', 'disk', 'battery']

print(df.isna().sum())

df['series'] = df["series"].fillna(' ')
df.fillna(-1, inplace=True)


def connect_elastic():
    client = Elasticsearch("http://localhost:9200")
    if client.ping():
        print("yay.. connected ")

    else:
        print("Cannot connect.")
    return client


def make_index(es_client, index_name, mappings):
    es_client.indices.create(index=index_name, ignore=400, body=mappings)
    return es_client


def put_record(es_client, index_name, doc, id):
    resp = es_client.index(index=index_name, id=id, document=doc)
    return resp


mappings = {
    "mappings": {
        "properties": {

            "brand": {
                "type": "keyword"
            },
            "id":{
                "type":"integer"
            },
            "series": {
                "type": "keyword"
            },
            "weight": {
                "type": "float"
            },
            "ram": {
                "type": "float"
            },
            "price": {
                "type": "float"
            },
            "disk": {
                "type": "float"
            },
            "battery": {
                "type": "float"
            }
        }
    }
}

# print(df)

# print(round((df.isna().sum()/len(df))*100,2))
data = df.to_dict('records')

### function to interate over the data


def generator(data):
    for i in data:
        i['_index'] = 'laptops'
        yield i


###  elastic instance
el = connect_elastic()

### creating index for the laptops with the defined mappings
# el= make_index(el,'laptops',mappings=mappings)
# print(el)


### upload the data to elastic search
# helpers.bulk(el, generator(data))


def update_user_vector(prev_vec, change_dict):
    prev_vec[change_dict["index"]] = change_dict["value"]
    return prev_vec


question1 = "How often you travell along with your laptop?"
print(question1)

q1_options = {
    "0": {
        "text": "yes, I travell a lot.",
        "change": {
            "index": 2,
            "value": 1.5
        }
    },
    "1": {
        "text": "Not much, Usaully stay at my desk.",
        "change": {
            "index": 2,
            "value": 3
        }
    },
    "2": {
        "text": "Do not have any specification .",
        "change": {
            "index": 2,
            "value":-1
        }
    },

}

print("0 : yes, I travell a lot.")
print("1 : Not much, Usaully stay at my desk.")
print("2 : Do not have any specification .")

inp = input()
