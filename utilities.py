import uuid
def generate_uuid():
    # make a UUID using a SHA-1 hash of a namespace UUID and a name
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org'))



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
