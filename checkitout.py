from elasticsearch import Elasticsearch

def connect_elastic():
    client = Elasticsearch("http://localhost:9200")
    if client.ping():
        print("yay.. connected ")

    else:
        print("Cannot connect.")
    return client

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


def cosine_in_elastic_search(index_name: str, query_vector: list, no_of_values: int, filter_name = '' ,filter_value =''):
    '''
        args: 
            index_name: database name or index name in es tems
            query_vector: users vector 
            no_of_values: how many recommendations he want
            filter_name: if the user wants to search based on the brand
            filter_value: the filter string which we need to check on the similar products

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

    if filter_name and filter_value:
        search_query['query']['script_score']['query'] ={'match':{filter_name: filter_value}}

    responses = es.search(index=index_name, body=search_query)
    # similarities = []
    return responses['hits']['hits']
    # for data in responses['hits']['hits']:
    #     response_to_be_shown = {
    #         "brand": data['_source']['brand'],
    #         "series": data['_source']['series'],
    #         "price": data['_source']['price'],
    #         "url": data['_source']['url'],
    #         'rating': float(data['_source']['rating'][:3]),
    #         "image_url": data['_source']['image_url'],
    #         "display": data['_source']["display"]
                
    #     }
    #     similarities.append(response_to_be_shown)
    # return similarities


print()
print()
data = cosine_in_elastic_search('laptop_recommendations',[1,1.5,1.2,1,1.4,1.12,1.56,1.32,2],10)
for i in data:
    print(i['_source'])
    print()
    print()
