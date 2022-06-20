from locale import normalize
import pandas as pd

df = pd.read_csv('full_processed.csv')





# copy the data
df = df[['weight','ram','price','graphics','disk','battery','display','processor','max_memory']]

  
# print(df_min_max_scaled)
# apply normalization techniques
# for column in df_min_max_scaled.columns:

#     df_min_max_scaled[column] = (df_min_max_scaled[column] - df_min_max_scaled[column].min()) / (df_min_max_scaled[column].max() - df_min_max_scaled[column].min())    
  
# view normalized data
# print(df_min_max_scaled)


def normalise_min_max(df):
    '''
    df all cols should be numerical 
    note: normalising values between 1 to 2
    '''
    # new_df= pd.DataFrame()
    for column in df.columns:
        df[column+"_norm"] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())+1
    return df



print(normalise_min_max(df))