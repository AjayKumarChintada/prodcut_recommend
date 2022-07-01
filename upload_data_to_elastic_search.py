from elasticsearch import Elasticsearch, helpers
import pandas as pd


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


def generator(data, index_name):
    for i in data:
        i['_index'] = index_name
        i['vector'] = [i['weight_norm'], i['ram_norm'], i['price_norm'], i['graphics_norm'],
                       i['disk_norm'], i['battery_norm'], i['display_norm'], i['processor_norm'], i['max_memory_norm']]
        yield i


def make_records(file_name):

    df = pd.read_csv(file_name)
    user_vec_ES = [df['weight_norm'].mean(), df['ram_norm'].median(), df['price_norm'].median(), df['graphics_norm'].median(),
                   df['disk_norm'].median(), df['battery_norm'].median(), df['display_norm'].median(), df['processor_norm'].median(), df['max_memory_norm'].median()]
    user_vec_ES = [str(i) for i in user_vec_ES]

    ## creating default vectors for refernece in future
    with open('default_vector_values.txt', 'w') as file:
        file.write("|".join(user_vec_ES))

    print("File : default_vector_values.txt  with default vectors created...")
    return df.to_dict('records')


def main():

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
                },
                "rating": {
                    "type": "text"
                },
                "image_url": {
                    "type": "text"
                }
            }
        }
    }
    ## index name
    # index_name = input("Enter index_name: ")
    index_name = 'laptop_recommendations'
    el = connect_elastic()

    print("Creating index with defined mappings for the dataset..")
    el = make_index(el, index_name, mappings=mappings)
    records = make_records('updated_dataset.csv')
    generator_data = generator(records, index_name)
    print(' uploading the data to elastic search....')
    ## uploading the data to elastic search....
    helpers.bulk(el, generator_data)

    print("Finished uploading ....")
    print()


main()
