import pandas as pd
import streamlit as st


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


def timeframe_fields(pre_fix, conditions, is_money=False):
    '''Takes prefix and conditions, returns fields for pipeline.py'''
    fields = {}
    if is_money:
        for suffix, condition in conditions.items():
            fieldname = f"anzahl_{pre_fix}_{suffix}"
            fields[fieldname] = {"$sum": {"$cond": [condition, "$amount", 0]}}
    else:
        for suffix, condition in conditions.items():
            fieldname = f"anzahl_{pre_fix}_{suffix}"
            fields[fieldname] = {"$sum": {"$cond": [condition, 1, 0]}}
    return fields


def cond_cat(extra_field, extra_value, pipe_dict):
    '''Creates a dict from 'condition', and appends 'extra_filed' & 'extra_value' to the output name. \n 
    Also compares if they are eq to condition'''
    result = {}
    for suffix, condition in pipe_dict.items():
        result[suffix] =  {"$and": [condition, {"$eq": [f"${extra_field}", extra_value]}  ]}
    return result


exception_cols = [
    "name", 
    "joker_tage_aktiviert", 
    "created_at", 
    "loeschstatus", 
    "kuendigungsstatus", 
    "status",
    "invoicing_start_date",
    "invoicing_cancellation_date"
    ]
