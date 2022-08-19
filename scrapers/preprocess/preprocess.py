import pandas as pd

df = pd.read_csv('processed_product_data.csv')


def preprocess(df):
    df['Weight'] = df['Weight'].fillna(df['Weight'].mean())
    df['RAM'] = df['RAM'].fillna(df['RAM'].median())
    df['price'] = df['price'].fillna(df['price'].mean())
    df['Graphics'] = df['Graphics'].fillna(0)
    df['Disk'] = df['Disk'].fillna(df['Disk'].median())
    df['Battery'] = df['Battery'].fillna(df['Battery'].median())
    df['Display'] = df['Display'].fillna(df['Display'].median())
    df['Processor'] = df['Processor'].fillna(df['Processor'].median())
    df['Max_Memory_Support'] = df['Max_Memory_Support'].fillna(
        df['Max_Memory_Support'].median())
    df['Series'] = df['Series'].fillna('')

    return df


df = preprocess(df)
df.to_csv('full_processed.csv', index=False)
