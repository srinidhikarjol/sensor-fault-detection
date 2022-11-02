from logging import exception
import  pymongo
from sensor.constant.database import DATABASE_NAME
import certifi,os
from sensor.constant.env_variables import MONGODB_URL_KEY
ca = certifi.where()

class MongoDBClient:
    client = None
    def __init__(self,database_name=DATABASE_NAME) -> None:
        try:
            if MongoDBClient.client is None:
                mongo_db_url = os.getenv(MONGODB_URL_KEY)
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
            self.client = MongoDBClient.client
            self.database = self.client[database_name]
            self.database_name = database_name 
        except Exception as e:
            raise e           