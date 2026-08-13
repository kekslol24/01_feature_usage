import pandas as pd

def df_creator(db, collection: str ,pipe):
    '''Creates dataframes from pymongo queries and returns them.'''
    array = list(db[collection].aggregate(pipe))
    df = pd.DataFrame(array)
    return df

def merger(df_one, df_two, on, how):
    '''Allows to merge two dataframes into one.'''
    merged_df = pd.merge(df_one, df_two, on=on, how=how)
    return merged_df

def merge_alle(dataframes, on, how):
    '''Takes multiple dataframes and merges them, if name-col
    appears multiple times, it just keeps one'''
    result = dataframes[0]
    for df in dataframes[1:]:
        if "name" in df.columns:
            df = df.drop(columns="name")
        result = merger(result, df, on, how)
    return result
