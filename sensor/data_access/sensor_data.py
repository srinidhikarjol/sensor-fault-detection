import sys
from typing import Optional

import numpy as np
import pandas as pd

from sensor.configuration.mongo_db_connection import MongoDBClient
from sensor.constant.database import DATABASE_NAME
from sensor.exception import SensorException

"""
To connect to the mongodb client and get the data
""" 
class SensorData:
    """
    This class will connent to mongoDb client, gets the collection and
    converts this to a dataframe.
    """

    def __init__(self) -> None:
        try:
            self.mongo_client =  MongoDBClient(database_name=DATABASE_NAME)
        except Exception as e:
            raise SensorException(e,sys)

    def export_collection_to_data_frame( self, collection_name: str,
     database_name: Optional[str] = None) -> pd.DataFrame :
        try:
            if database_name is None:
                collection = self.mongo_client.database[collection_name]
            else:
                collection = self.mongo_client[database_name][collection_name]


            # convert collection to dataframe
            df = pd.DataFrame(list(collection.find()))

            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)

            df.replace({"na": np.nan}, inplace=True)

            return df
    
        except Exception as e:
            raise SensorException(e,sys)