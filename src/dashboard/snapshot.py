import pandas as pd
from src.lib import pipelines
from src.lib import helpers
import pymongo
import os
from dotenv import load_dotenv
import pyarrow

load_dotenv()

mongo_uri = os.getenv("mongo_uri")
client = pymongo.MongoClient(mongo_uri)

db = client["klapp-prod"]

pipeline_list = pipelines.pipeline_list


def main():
    all_dfs = []
    for pipe, collection in pipeline_list:
        df = helpers.df_creator(db, collection, pipe)
        all_dfs.append(df)

    merged = helpers.merge_alle(all_dfs, on="_id", how="outer")
    merged = merged.drop(columns="_id")
    exception_cols = ["name", "joker_tage_aktiviert"]
    digit_cols = merged.columns.difference(exception_cols)
    merged[digit_cols] = merged[digit_cols].fillna(0)
    merged[digit_cols] = merged[digit_cols].astype(int)

    merged.to_parquet("data/snapshot.parquet", index=False)


if __name__ == "__main__":
    main()