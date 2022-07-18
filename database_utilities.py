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


  def column_min_max(self,filter_name):
    """get min and max values of filter to normalise the data 

    Args:
        filter_name (string): filter name 
    """
    max_doc = list(self.connect_to_collection().find().sort(filter_name, -1).limit(1))
    min_doc = list(self.connect_to_collection().find().sort(filter_name, 1).limit(1))
    max_doc.extend(min_doc)
    # return max_doc.extend(min_doc)
    return max_doc

    

# config = read_default_values('config.json')

# db = Database(config['db_url_local'],config['db_name'],config['dataset_collection'])
# for i in db.column_min_max('price'):
#   print(i)

