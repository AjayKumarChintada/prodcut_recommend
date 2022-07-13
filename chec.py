# a = {
#     "filter": 'battery'
#     "value": 6.0,
#     "metric": 'hrs'
#     ''
# }
# b = []


# output = [
#     {
#         "battery" : 6.0
#     },
#     {
#         'screen': 1
#     },
#     {
#         'weight': 2.51
#     }


# ]


# def make_filter_object(a):

#     myDict = [{x: a[x]} for x in a]


# make_filter_object(a)


# # printing original dictionary
# print("The original dictionary : " + str(test_dict))

# # Using items() + len() + slice()
# # Split dictionary by half
# inc = iter(test_dict.items())
# res1 = dict(islice(inc, len(test_dict) // len(test_dict)))
# res2 = dict(inc)

# # printing result
# print("The first half of dictionary : " + str(res1))
# print("The second half of dictionary : " + str(res2))


a = [
    ['weight', 1.07,'kg','~'],
    ['battery',11.5,'hrs','~'],
]


vals = ['weight', 1.07]

metrics = {
    'weight': {
        "operator": '~',
        "metric": "Kg"},

    'battery': {
        "operator": '~',
        "metric": "Hours"},

    'screen_size': {
        "operator": '~',
        "metric": "Inches"},

},


def make_filter_object(array:list):
    """ returns list of dictionaries or filter objects
    Args:
        array (list): list of list
    """
    data = []
    for resp in array: 
        metrics = {
            'filter': resp[0],
            "operator":resp[1],
            "metric": resp[2],
            'value': resp[3]
        }

        data.append(metrics)
    return data


# print(make_filter_object(a))


obj = [
    {
        "filter": "price",
        "metric": "INR",
        "operator": 19990,
        "value": "~"
    },
    {
        "filter": "battery",
        "metric": "INR",
        "operator": 19990,
        "value": "~"
    }
]

b = {
        "filter": "battery",
        "metric": "INR",
        "operator": 19990,
        "value": "~"
    }


def search_and_get_index(obj,b):
    for indexval in range(len(obj)):
        if b['filter'] == obj[indexval]['filter']:
            return 1,indexval
    return 0

import pandas as pd
import json

def get_default_values(filename):
    created_file_name = 'default_vector_values.json'
    df = pd.read_csv(filename)
    df = df[['weight_norm','ram_norm','price_norm','graphics_norm','disk_norm','battery_norm','display_norm','processor_norm','max_memory_norm']]
    data_dictionary = {}
    for i in df.columns:
        data_dictionary[i.split('_norm')[0]] = df[i].median()
    print(data_dictionary)
    with open(created_file_name, "w") as outfile:
        json.dump(data_dictionary, outfile)
    print('default_vector_values.json file created in the current directory..')
    return created_file_name

def read_default_values(filename):
    with open(filename,'r') as file:
        data = json.load(file)
        return data

dictionary = read_default_values('default_vector_values.json')
print(dictionary)


def get_index_and_value(dicitionary,key):

    keys = list(dictionary.keys())
    index_val,value = keys.index(key),dicitionary[key]
    return index_val,value

# print(get_index_and_value(dicitionary=dictionary,key='ram'))




