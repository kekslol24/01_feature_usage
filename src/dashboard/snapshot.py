import pandas as pd
from src.lib import pipelines
from src.lib import helpers
import pymongo
import os
from dotenv import load_dotenv
# import pyarrow

load_dotenv()

mongo_uri = os.getenv("mongo_uri")
client = pymongo.MongoClient(mongo_uri)

db = client["klapp-prod"]

pipeline_list = pipelines.pipeline_list


def main():
    all_dfs = []
    ### create df from pipes, collections and db
    for pipe, collection in pipeline_list:
        df = helpers.df_creator(db, collection, pipe)
        all_dfs.append(df)

    ### merge newly created df into one
    merged = helpers.merge_alle(all_dfs, on="_id", how="outer")
    merged = merged.drop(columns="_id")

    ### extract non digit columns
    digit_cols = merged.columns.difference(helpers.exception_cols)

    ### convert digit columns to int
    merged[digit_cols] = merged[digit_cols].fillna(0)
    merged[digit_cols] = merged[digit_cols].astype(int)

    ### convert non standardized datetimes to datetime
    merged["invoicing_start_date"] = pd.to_datetime(merged["invoicing_start_date"], errors="coerce", utc=True)
    merged["invoicing_cancellation_date"] = pd.to_datetime(merged["invoicing_cancellation_date"], errors="coerce", utc=True)

    ### generate snapshot
    merged.to_parquet("data/snapshot.parquet", index=False)


if __name__ == "__main__":
    main()