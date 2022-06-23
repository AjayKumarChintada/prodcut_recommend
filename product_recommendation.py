
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
    for resp in responses['hits']['hits']:
        similarities.append(resp)
    return similarities


def update_vector_with_choices(question_num, choice_num):

    question_filters = {
        0: {
            # indexes:  weight battery screensize
            #option number: [[index,replacements]

            0: [[0, 5, 6], [1, 1.75, 1.75]],
            1: [[0, 5, 6], [1.75, 1.2, 2]],
            2: [[0, 5, 6], []]
        },
        ## RAM, Graphic ram, processor speed
        1: {

            0: [[1, 3, -2], [2, 1.75, 2]],
            1: [[1, 3, -2], [1, 1, 1]],
            2: [[1, 3, -2], [1.5, 1.4, 1.5]]


        },
        ## price
        2: {
            0: [[2], [1]],
            1: [[2], [1.5]],
            2: [[2], [2]]

        },
        ## disk size, max memory support
        3: {
            0: [[4, 8], [2, 2]],
            1: [[4, 8], [1, 1]],
            2: [[4, 8], [1.5, 1.5]]
        }
    }

    return question_filters[question_num][choice_num]


def update_vector(arr, indexes, values):
    ## to keep the default values same when user have no specifications
    if not values:
        return arr
    for i in range(len(indexes)):
        arr[indexes[i]]= values[i]
    return arr


def main():
    user_vec_ES = get_default_vector()
    print("Default Vector: ", user_vec_ES)
    question_num = int(input("Enter Qestion number: "))
    choice_num = int(input('Enter Choice number: '))
    indexes, filters = update_vector_with_choices(
        question_num=question_num, choice_num=choice_num)
    user_vec_ES = update_vector(user_vec_ES, indexes=indexes, values=filters)
    print(user_vec_ES)



main()

























## get variances
# print("-----Variances----")
# noramalisation_variance_vals = df[['weight_norm','ram_norm','price_norm','graphics_norm','disk_norm','battery_norm','display_norm','processor_norm','max_memory_norm']]
# print(noramalisation_variance_vals.var())
# noramalisation_variance_vals.boxplot()

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


# df = pd.read_csv('full_processed.csv')
# # df = preprocess(df)
# df = normalise_min_max(df[['weight', 'ram', 'price', 'graphics',
#                            'disk', 'battery', 'display', 'processor', 'max_memory']])

# df = result = pd.concat([df, df], axis=1, join='inner')
# print(df.head(10))


# print("Default vector: ", user_vec_ES)

# ##### imported code
# question1 = "How often you travell along with your laptop?"
# print(question1)
# # weight battery screensize

# # q1_options = {
# #     "0": {
# #         "text": "yes, I travell a lot.",
# #         "change":
# #          {
# #              "index": [0, 5, 6],
# #             "value": [1, 1.75, 1.75]
# #          }

# #     },

# #     "1": {
# #         "text": "Not much, Usaully stay at my desk.",
# #         "change":
# #          {
# #              "index": [0, 5, 6],
# #              "value": [1.75, 1.2, 2]
# #          }
# #     },

# #     "2":
# #     {
# #         "text": "Do not have any specification .",
# #         "change":
# #         {

# #                 "index": [0, 5, 6],
# #                 #not adding any signicant change since already initialised with the medians
# #                 "value": [user_vec_ES[0], user_vec_ES[5],user_vec_ES[6]]
# #         }
# #     }


# # }

# # print("0 : yes, I travell a lot.")
# # print("1 : Not much, Usaully stay at my desk.")
# # print("2 : Do not have any specification.")

# # inp = input()
# # user_vec = update_user_vector(user_vec_ES, q1_options[inp]["change"])
# # print("user vec after q1", user_vec)

# # #calling the cosine function
# # # print(cosine_in_elastic_search('laptop_recommendations',user_vec_ES,4))

# # question2 = "What is your laptop typically used for ?"
# # print(question2)
# # # RAM, Graphic ram, processor speed
# # q2_options = {
# #     "0": {
# #         "text": "gaming and media development",
# #         "change":
# #          {
# #              "index": [1, 3, -2],
# #                 "value": [2, 1.75, 2]
# #          }
# #     },
# #     "1": {
# #         "text": "office and general business purpose",
# #         "change": {
# #             "index": [1, 3, -2],
# #             #if no graphis its 0
# #             "value": [1, 1, 1]
# #         }
# #     },
# #     "2": {
# #         "text": "student usage/design and development",
# #         "change": {
# #             "index": [1, 3, -2],
# #             "value": [1.5, 1.4, 1.5]
# #         }
# #     },

# # }

# # print("0 : gaming and media development")
# # print("1 : office and general business purpose")
# # print("2 : student usage/design and development")

# # inp = input()
# # user_vec = update_user_vector(user_vec_ES, q2_options[inp]["change"])

# # print("user vec after q2", user_vec)
# # # print(cosine_in_elastic_search('laptop_recommendations',user_vec_ES,4))


# # question3 = "What is the price range you want for your laptop ?"
# # print(question3)
# # # price

# # q3_options = {
# #     "0": {
# #         "text": "less than 30000 / low range",
# #         "change":
# #          {
# #              "index": [2],
# #                 "value": [1]
# #          }
# #     },
# #     "1": {
# #         "text": "30000 to 50000 / mid range",
# #         "change": {
# #             "index": [2],
# #             "value": [1.5]
# #         }
# #     },
# #     "2": {
# #         "text": "more than 50000 / high range",
# #         "change": {
# #             "index": [2],
# #             "value": [2]
# #         }
# #     },

# # }

# # print("0 : less than 30000")
# # print("1 : 30000 to 50000")
# # print("2 : more than 50000")

# # inp = input()
# # user_vec = update_user_vector(user_vec_ES, q3_options[inp]["change"])

# # print("user vec after q3", user_vec)

# # print(cosine_in_elastic_search('laptop_recommendations',user_vec_ES,4))


# # question4 = "Do you store a lot of content in your device?"
# # print(question4)
# # # disk size, max memory support

# # q4_options = {
# #     "0": {
# #         "text": "Yes, a lot. Need large storages",
# #         "change":
# #          {
# #              "index": [4, 8],
# #              "value": [2, 2]
# #          }
# #     },
# #     "1": {
# #         "text": "No I dont. Use it only for official purposes",
# #         "change": {
# #             "index": [4, 8],
# #             "value": [1, 1]
# #         }
# #     },
# #     "2": {
# #         "text": "Moderate usage, nothing specific. Anything works",
# #         "change": {
# #             "index": [4, 8],
# #             "value": [1.5, 1.5]
# #         }
# #     },

# # }

# # print("0 : Yes, a lot. Need large storages")
# # print("1 : No I dont. Use it only for official purposes")
# # print("2 : Moderate usage, nothing specific. Anything works")

# # inp = input()
# # user_vec = update_user_vector(user_vec_ES, q4_options[inp]["change"])
# # print("user vec after q4", user_vec)

# # print(cosine_in_elastic_search('laptop_recommendations',user_vec_ES,4))
