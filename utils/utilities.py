import uuid
def generate_uuid():
    # make a UUID using 4 with random 
    return str(uuid.uuid4())



def update_filter_values(index,filters,new_filter):
    filter_to_be_updated = filters[index]
    for key in new_filter:
        if key in filter_to_be_updated:
            filter_to_be_updated[key] = new_filter[key]
        else:
            return 0
    filters[index] = filter_to_be_updated
    return filters


def make_filter_object(array: list):
    """ returns list of dictionaries or filter objects
    Args:
        array (list): list of list
    """
    data = []
    for resp in array:
        metrics = {
            'filter': resp[0],
            'value': resp[1],
            "operator": resp[3],
            "metric": resp[2]
        }
        data.append(metrics)
    return data

def search_and_get_index(filters, filter):
    """search for same filter and returns 1 and its index value if found else 0

    Args:
        obj (filters oject list): list of filter objects
        b (single object): a single filter object to search

    Returns:
        (1,index_val)/ 0: tuple of index value and flag or 0
    """
    for indexval in range(len(filters)):
        if filter['filter'] == filters[indexval]['filter']:
            return 1, indexval
    return 0, None


def modify_response_laptop_data(laptop_data,filters):
    temp_data =[]
    filters = [i['filter']for i in filters]
    for laptop in laptop_data:
        default_data = {
            "brand": laptop['brand'],
            "series": laptop['series'],
            "price": laptop['price'],
            "url": laptop['url'],
            'rating': float(laptop['rating'][:3]),
            "image_url": laptop['image_url'],
            "display": laptop["display"]
        }
        for filter in filters:
            norm_filter = filter+'_norm'
            if norm_filter in laptop:
                default_data[filter+'_strength'] = strength(laptop[norm_filter])
        temp_data.append(default_data)
    return temp_data
    

def strength(normalised_value):
    old_value = normalised_value 
    old_min = 1
    old_max = 2
    new_max = 10
    new_min = 1
    OldRange = (old_max - old_min)  
    NewRange = (new_max - new_min)  
    strength_val = (((old_value - old_min) * NewRange) / OldRange) + new_min
    # strength_val = ( (old_value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min
    return round(strength_val)


def get_indexes_values_from_db(data,choice_number):
    return data["index_values"],data[choice_number]