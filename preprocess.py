
import pandas as pd
from elasticsearch import Elasticsearch, helpers
import json


def normalise_min_max(df):
    '''
    df all cols should be numerical 
    note: normalising values between 1 to 2
    '''
    new_df = pd.DataFrame()
    for column in df.columns:
        new_df[column+"_norm"] = (df[column] - df[column].min()) / \
            (df[column].max() - df[column].min())+1
    return new_df


# def preprocess(df):
#     df['Weight'] = df['Weight'].fillna(df['Weight'].mean())
#     df['RAM'] = df['RAM'].fillna(df['RAM'].median())
#     df['price'] = df['price'].fillna(df['price'].mean())
#     df['Graphics'] = df['Graphics'].fillna(0)
#     df['Disk'] = df['Disk'].fillna(df['Disk'].median())
#     df['Battery'] = df['Battery'].fillna(df['Battery'].median())
#     df['Display'] = df['Display'].fillna(df['Display'].median())
#     df['Processor'] = df['Processor'].fillna(df['Processor'].median())
#     df['Max_Memory_Support'] = df['Max_Memory_Support'].fillna(
#         df['Max_Memory_Support'].median())
#     df['Series'] = df['Series'].fillna('')
#     return df
df = pd.read_csv('full_processed.csv')
# df = preprocess(df)
new_df = normalise_min_max(df[['weight', 'ram', 'price', 'graphics',
                           'disk', 'battery', 'display', 'processor', 'max_memory']])

df = result = pd.concat([df, new_df], axis=1, join='inner')
print(df)


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


mappings = {
    "mappings": {
        "properties": {
            "id": {
                "type": "integer"
            },

            "brand": {
                "type": "keyword"
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
            "graphics": {
                "type": "float"
            },
            "disk": {
                "type": "float"
            },
            "battery": {
                "type": "float"
            },
            "display": {
                "type": "float"
            },
            "processor": {
                "type": "float"
            },
            "max_memory": {
                "type": "float"
            },

            "url": {
                "type": "text"
            },
            "vector": {
                "type": "dense_vector",
                "dims": 9
            }
        }
    }
}


df['series'] = df['series'].fillna('laptop')

df.to_csv('updated_dataset.csv', index=False)


data = df.to_dict('records')


# ###  elastic instance


def generator(data):
    for i in data:
        i['_index'] = 'laptop_recommendations'
        i['vector'] = [i['weight_norm'], i['ram_norm'], i['price_norm'], i['graphics_norm'],
                       i['disk_norm'], i['battery_norm'], i['display_norm'], i['processor_norm'], i['max_memory_norm']]
        yield i


# # ### creating index for the laptops with the defined mappings
el = connect_elastic()
# el= make_index(el,'laptop_recommendations',mappings=mappings)
# print(el)


### uploaded the data to elastic search

# helpers.bulk(el, generator(data))


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


#default user vector
user_vec_ES = [new_df['weight_norm'].mean(), new_df['ram_norm'].mean(), new_df['price_norm'].mean(), new_df['graphics_norm'].mean(),
               new_df['disk_norm'].mean(), new_df['battery_norm'].mean(), new_df['display_norm'].mean(), new_df['processor_norm'].mean(), new_df['max_memory_norm'].mean()]


def cosine_in_elastic_search(es, index_name, query_vector):
    '''
        args: 
            es: elastic search client
            index_name: database name or index name in es tems
            query_vector: users vector 

        returns: 
            responses: es object with cosine similarity matches of 7
    '''

    search_query = {
        "size": 20,
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

    for resp in responses['hits']['hits']:
        print(
            "Brand: {} - laptop series: {} - Score: {} ".format(resp['_source']['series'], resp['_source']['series'], resp['_score']))

        # print(resp)
        print(json.dumps(resp, indent=4))
        print('\n\n')


###### imported code
question1 = "How often you travell along with your laptop?"
print(question1)
# weight battery screensize

q1_options = {
    "0": {
        "text": "yes, I travell a lot.",
        "change":
         {
             "index": [0, 5, 6],
                "value": [1, 1.75, 1.75]
         }

    },

    "1": {
        "text": "Not much, Usaully stay at my desk.",
        "change":
         {
             "index": [0, 5, 6],
             "value": [1.75, 1.2, 2]
         }
    },

    "2":
    {
        "text": "Do not have any specification .",
        "change":
        {
                "index": [0, 5, 6],
                "value": [df['weight'].mean(), df['battery'].median(), df['display'].median()]
        }
    }



}

print("0 : yes, I travell a lot.")
print("1 : Not much, Usaully stay at my desk.")
print("2 : Do not have any specification.")

inp = input()
user_vec = update_user_vector(user_vec_ES, q1_options[inp]["change"])
print("user vec after q1", user_vec)

#calling the cosine function
cosine_in_elastic_search(el,'laptop_recommendations',user_vec_ES)

question2 = "What is your laptop typically used for ?"
print(question2)
# RAM, Graphic ram, processor speed
q2_options = {
    "0": {
        "text": "gaming and media development",
        "change":
         {
             "index": [1, 3, -2],
                "value": [2, 1.75, 2]
         }
    },
    "1": {
        "text": "office and general business purpose",
        "change": {
            "index": [1, 3, -2],
            #if no graphis its 0
            "value": [1, 1, 1]
        }
    },
    "2": {
        "text": "student usage/design and development",
        "change": {
            "index": [1, 3, -2],
            "value": [1.5, 1.4, 1.5]
        }
    },

}

print("0 : gaming and media development")
print("1 : office and general business purpose")
print("2 : student usage/design and development")

inp = input()
user_vec = update_user_vector(user_vec_ES, q2_options[inp]["change"])

print("user vec after q2", user_vec)
cosine_in_elastic_search(el,'laptop_recommendations',user_vec_ES)


question3 = "What is the price range you want for your laptop ?"
print(question3)
# price

q3_options = {
    "0": {
        "text": "less than 30000 / low range",
        "change":
         {
             "index": [2],
                "value": [1]
         }
    },
    "1": {
        "text": "30000 to 50000 / mid range",
        "change": {
            "index": [2],
            "value": [1.5]
        }
    },
    "2": {
        "text": "more than 50000 / high range",
        "change": {
            "index": [2],
            "value": [2]
        }
    },

}

print("0 : less than 30000")
print("1 : 30000 to 50000")
print("2 : more than 50000")

inp = input()
user_vec = update_user_vector(user_vec_ES, q3_options[inp]["change"])

print("user vec after q3", user_vec)

cosine_in_elastic_search(el,'laptop_recommendations',user_vec_ES)


question4 = "Do you store a lot of content in your device?"
print(question4)
# disk size, max memory support

q4_options = {
    "0": {
        "text": "Yes, a lot. Need large storages",
        "change":
         {
             "index": [4, 8],
             "value": [2, 2]
         }
    },
    "1": {
        "text": "No I dont. Use it only for official purposes",
        "change": {
            "index": [4, 8],
            "value": [1, 1]
        }
    },
    "2": {
        "text": "Moderate usage, nothing specific. Anything works",
        "change": {
            "index": [4, 8],
            "value": [1.5, 1.5]
        }
    },

}

print("0 : Yes, a lot. Need large storages")
print("1 : No I dont. Use it only for official purposes")
print("2 : Moderate usage, nothing specific. Anything works")

inp = input()
user_vec = update_user_vector(user_vec_ES, q4_options[inp]["change"])
print("user vec after q4", user_vec)

cosine_in_elastic_search(el,'laptop_recommendations',user_vec_ES)
