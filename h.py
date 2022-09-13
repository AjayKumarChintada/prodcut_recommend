# data = {
#     "0": [
#         2,
#         1,
#         1.5
#     ],
#     "1": [
#         2,
#         1,
#         1.5
#     ],
#     "_id": 1,
#     "index_values": [
#         1,
#         3,
#         2
#     ]
# }

# def get_indexes_values_from_db(data,choice_number):
#     return data["index_values"],data[choice_number]

# # print(get_indexes_values_from_db(data,"1"))

# # Creates a sorted dictionary (sorted by key)
# from collections import OrderedDict

# dict = {'suraj': '32','ravi': '10','yash': '100', }

# dict = OrderedDict(sorted(dict.items()))
# print(dict)
# print(list(dict.keys()))




a = ['a','b','c','d','aa','']
a = [i for i in a if not i.startswith('a')and i]
print(a)