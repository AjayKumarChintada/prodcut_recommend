# %%
import json
import os
import re

import numpy as np
import pandas as pd
from scipy import stats

from utils.database_utilities import Database

direcotry = os.path.join(os.getcwd(),'admin','uploaded_files','tv_data_set.csv')
DB_URL = "mongodb://localhost:27017/"
DB_NAME = "tvs"
questions_collection = 'questions'
options_collection = 'options'
min_max_collection = 'min_max_filter_values'
dataset_collection = 'dataset'


def null_percentage(df):
    percent_missing = df.isnull().sum() * 100 / len(df)
    missing_value_df = pd.DataFrame({'percent_missing': percent_missing})
    missing_value_df.reset_index(inplace=True)
    missing_value_df.columns = ['column_name','percent_missing']
    missing_value_df = missing_value_df.sort_values('percent_missing',)
    return missing_value_df

def show_columns(path_to_file):
    df = pd.read_csv(path_to_file, index_col = False)
    #to remove unnamed cols
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.drop(['id'],axis=1,inplace=True)
    missing_value_df = null_percentage(df)
    ##considering only the features which has data greater than 70
    missing_value_df = missing_value_df[missing_value_df['percent_missing']<70]
    required_columns = list(missing_value_df.column_name)
    df = df[required_columns]
    df.columns = df.columns.str.replace(' ','_')
    df.columns = df.columns.str.lower()
    return df, list(df.columns)
    


df = show_columns(direcotry)[0]
# %%
###on showing all the columns SME will give us features selected by sme and product information as payload
##INPUTS 

PROJECT_NAME = ""
FEATURES_SELECTED_BY_SME = ['price','refresh_rate','audio_wattage','maximum_operating_distance','brand','resolution','rating',
'standing_screen_display_size','display_technology','item_weight','wattage','supports_bluetooth_technology']

PRODUCT_INFORMATION = ['image_url','product','product_url']

ALL_COLUMNS = sorted(FEATURES_SELECTED_BY_SME + PRODUCT_INFORMATION)
# print(ALL_COLUMNS)

df = df.loc[:,ALL_COLUMNS]


# %%
missing_value_df = null_percentage(df)
missing_value_df

# %%


def extract_data_before_first_space(string):
    if string is not np.NaN:
        return float(re.split(" +", str(string))[0])
    return string
    
    
def remove_word_from_string(string,word):
    words =string.split(word)
    words = [i.strip() for i in words]
    return ' '.join(words).strip()



def weight_processor(weight_string):
    """
    takes - weight_string
        ex: 1 kg 200 g, 
    returns - weight in kg with no units
        ex: 1.2000
    """
    # can handle, 1 kg 200 g, 1.2 kg 
    pattern1 = r".*(\b\d+).*(\b\d+).*"
    # can handle 1 kg, 2 kg
    pattern2 = r".*(\b\d+).*"

    result_pat1 = re.search(pattern1, weight_string)

    if result_pat1:
        groups = result_pat1.groups()
        kg = float(groups[0])
        gm = float(groups[1])
        return kg + gm / 1000
        # return float(groups[0] + "." + groups[1])
    
    result_pat2 = re.search(pattern2, weight_string)

    if result_pat2:
        groups = result_pat2.groups()
        weight = float(groups[0])
        if weight > 100:
            return weight / 1000
        return float(weight)

# %%
def resolution_process(resolution_string):
    if 'x' in resolution_string:
        [i,j] = resolution_string.split('x',2)
        res = float(i)*float(j)
        return(res)
    return None

# %%
try:

    df['rating'] = df['rating'].apply(lambda x: extract_data_before_first_space(x))
    df['refresh_rate'] = df['refresh_rate'].apply(lambda x: extract_data_before_first_space(x))
    df ['audio_wattage'] = df['audio_wattage'].apply(lambda x: extract_data_before_first_space(x))
    df ['resolution'] = df['resolution'].apply(lambda x : remove_word_from_string(x,'Pixels'))
    df['standing_screen_display_size'] = df['standing_screen_display_size'].apply(extract_data_before_first_space)
    df['maximum_operating_distance'] = df['maximum_operating_distance'].apply(extract_data_before_first_space)
    df['wattage'] = df['wattage'].apply(extract_data_before_first_space)
    df['item_weight'] = df['item_weight'].apply(lambda x: weight_processor(str(x)))
    df['resolution'] = df['resolution'].apply(lambda x: resolution_process(str(x)))
    df['price'] = df['price'].str.replace(',', '').astype('float')
except Exception as  ex :
    print("preprocessing failed for this dataset")





# %%
##filling null values 
###better implementing them based on data type

# df['refresh_rate'] = df['refresh_rate'].fillna(df['refresh_rate'].median())
# df['display_type']= df['display_type'].fillna(df['display_type'].mode()[0])
# df['audio_wattage'] = df['audio_wattage'].fillna(df['audio_wattage'].mean())
# df['maximum_operating_distance'] = df['maximum_operating_distance'].fillna(df['maximum_operating_distance'].mean())
# df['resolution'] = df['resolution'].fillna(df['resolution'].mean())
# df['rating'] = df['rating'].fillna(df['rating'].median())
# df['standing_screen_display_size'] = df['standing_screen_display_size'].fillna(df['standing_screen_display_size'].mean())
# df['display_technology'] = df['display_technology'].fillna(df['display_technology'].mode()[0])
# df['wattage'] = df['wattage'].fillna(df['wattage'].median())
# df['item_weight'] = df['item_weight'].fillna(df['item_weight'].mean())
# df['supports_bluetooth_technology'] = df['supports_bluetooth_technology'].fillna(df['supports_bluetooth_technology'].mode()[0])


df_types = df.dtypes.apply(lambda x: x.name).to_dict()  

categorical_values = [ i for i in df_types if df_types[i] =='object']
##ask for product information by showing categories and keep the remaining as either boolean if 2 or keep them as ENUM
# columns for product information will be coming from admin 

def categories_enum_or_boolean(df,column):
    return df[column].value_counts().size == 2


#seggregating the data type of features
CATEGORICAL_FEATURES = list(set(categorical_values).difference(set(PRODUCT_INFORMATION)))
BOOLEAN_COLS = []
ENUM_COLS = []

for i in CATEGORICAL_FEATURES:
    if categories_enum_or_boolean(df,i):
        BOOLEAN_COLS.append(i)
    else:
        ENUM_COLS.append(i)
#divide what are booleans and what are enums

VECTOR_FEATURES = list(set(df_types.keys()).difference(set(CATEGORICAL_FEATURES+PRODUCT_INFORMATION)))

##sorted values to keep their index positions secure
DATA_TYPE_DICTIONARY = {'Number':sorted(VECTOR_FEATURES),'Enum':sorted(ENUM_COLS),'Boolean':sorted(BOOLEAN_COLS)}


##converting Booleans to 1 and 0 
for boolean_column in DATA_TYPE_DICTIONARY['Boolean']:
    value1,value2 = df[boolean_column].value_counts().index.to_list()
    df[boolean_column]= df[boolean_column].map({value1:1, value2:0})
    # print(boolean_column)


with open("data_type_dictionary.json", "w") as outfile:
    json.dump(DATA_TYPE_DICTIONARY, outfile)


##imputing null values 
for datatype in DATA_TYPE_DICTIONARY:

    if datatype =='Number':
        for col in DATA_TYPE_DICTIONARY[datatype]:
            df[col] = df[col].fillna(df[col].mean())
    else:
        for col in DATA_TYPE_DICTIONARY[datatype]:
            df[col] = df[col].fillna(df[col].mode()[0])



##remove outliers which are out of standard deviation 2

df = df[(np.abs(stats.zscore(df.select_dtypes(exclude='object'))) < 2).all(axis=1)]


# %%
## Now time to do min max normalisation
def normalise_min_max(df,numeric_columns):
    '''
    df all cols should be numerical 
    note: normalising values between 1 to 2
    '''
    # df = pd.DataFrame()
    for column in numeric_columns:
        # if df[column].dtype == float or  df[column].dtype == int  :
        df[column+"_norm"] = ((df[column] - df[column].min()) /(df[column].max() - df[column].min())+1)
    return df


# %%

db = Database(DB_URL,DB_NAME,min_max_collection)
##making the min_max_filters into the db
for datatype in DATA_TYPE_DICTIONARY:
    if datatype in ["Number", "Boolean"]:
        for filter_name in DATA_TYPE_DICTIONARY[datatype]:
            min_val, max_val = float(df[filter_name].min()), float(
                df[filter_name].max())
            object_to_be_inserted = {
                "max_value": max_val,
                "min_value": min_val,
                "filter": filter_name,
                "data_type": datatype
            }
            db.connect_to_collection().insert_one(object_to_be_inserted)
    else:
        for filter_name in (DATA_TYPE_DICTIONARY[datatype]):
            enum_array = df[filter_name].value_counts().index.to_list()
            object_to_be_inserted={
            "values": enum_array,
            "filter": filter_name,
            "data_type": datatype
            }
            # print(object_to_be_inserted)
            db.connect_to_collection().insert_one(object_to_be_inserted)

        


# %%
##Normalisation happened
df_min_max = normalise_min_max(df,DATA_TYPE_DICTIONARY['Number'])


##push the data to datasets collection
dataset_to_db = Database(DB_URL,DB_NAME,dataset_collection)
dataset_to_db.insert_documents(df_min_max.to_dict('records'))



