import pymongo
from product_recommendation import read_default_values
class Database:
  def __init__(self, db_url, db_name, collection_name):
    self.db_url = db_url
    self.db_name = db_name
    self.collection_name = collection_name

  def connect_to_collection(self):
    """connects to a database with collection name

    Returns:
        cursor: db cursor object
    """
    client = pymongo.MongoClient(self.db_url)
    db = client[self.db_name]
    cursor = db[self.collection_name]
    return cursor

  def get_question_with_id(self, id_val):
    results = self.connect_to_collection().find_one({'_id': id_val})
    if results:
      return results
    return 0

  def get_last_record_id(self):
    cursor = list(self.connect_to_collection(
    ).find().sort("_id", -1).limit(1))[0]['_id']
    return cursor

  def insert_documents(self, documents):
    resp = self.connect_to_collection().insert_many(documents)
    print('data inserted successfully...')
    return resp


  def min_max_normalised_value(self,filter_name,value):
    """get min and max values of filter to normalise the data 

    Args:
        filter_name (string): filter name 
    """
    max_value = float(list(self.connect_to_collection().find().sort(filter_name, -1).limit(1))[0][filter_name])
    min_value = float(list(self.connect_to_collection().find().sort(filter_name, 1).limit(1))[0][filter_name])
    
    normalised_value = (value - min_value) / (max_value - min_value) + 1
    # print(max_value,min_value,normalised_value,"normalised_values")
    return normalised_value

  
    

    


