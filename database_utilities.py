import json
import pymongo



def get_database_connection(connection_url , data_base_name ):
  try:

    myclient = pymongo.MongoClient(connection_url)
    mydb = myclient[data_base_name]
    return mydb

  except Exception as e:
    print("Error occured during connection to db :--- ",e)



def connect_to_collection(db,collection_name):
  mycol = db[collection_name]
  return mycol

def insert_documents(collection_name,documents):
  resp = collection_name.insert_many(documents)
  print(resp)



connection_url = 'mongodb://localhost:27017/'
data_base_name = "product_recommendation"
collection_name = 'questions'

def get_question_with_id(id_val):
  connection_url = 'mongodb://localhost:27017/'
  data_base_name = "product_recommendation"
  collection_name = 'questions'

  db = get_database_connection(connection_url, data_base_name)
  questions_collection = connect_to_collection(db,collection_name) 
  results = questions_collection.find_one({'_id':id_val})
  if results:
    return results
  return 0

def get_last_record_id():
  connection_url = 'mongodb://localhost:27017/'
  data_base_name = "product_recommendation"
  collection_name = 'questions'
  db = get_database_connection(connection_url, data_base_name)
  questions_collection = connect_to_collection(db,collection_name)  
  cursor = list(questions_collection.find().sort("_id", -1).limit(1))[0]['_id']
  return cursor
  


question_dictionary = [
      {
          '_id': 0,
          'question': "How often you travell along with your laptop?",
          'options': ["yes, I travell a lot.", "Not much, Usaully stay at my desk.", "Do not have any specification .", ]
      },

      {
          '_id': 1,
          "question":  "What is your laptop typically used for ?",
          'options': ['gaming and media development', 'office and general business purpose', 'student usage/design and development']

      },

      {
          '_id': 2,
          "question": "What is the price range you want for your laptop ?",
          'options': ["less than 30000 / low range", "30000 to 50000 / mid range", "more than 50000 / high range"]

      },
      {
          '_id': 3,
          "question": "Do you store a lot of content in your device?",
          'options': ['Yes, a lot. Need large storages', 'No I dont. Use it only for official purposes', ' Moderate usage, nothing specific. Anything works']

      }

  ]
def insert_docs():
  connection_url = 'mongodb://localhost:27017/'
  data_base_name = "product_recommendation"
  collection_name = 'questions'
  db = get_database_connection(connection_url, data_base_name)
  questions_collection = connect_to_collection(db,collection_name)  
  insert_documents(questions_collection,question_dictionary)