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

# print(search_and_get_index(obj,b))
for indexval in range(len(obj)):
    if b['filter'] == obj[indexval]['filter']:
        del(obj[indexval])
print(obj)