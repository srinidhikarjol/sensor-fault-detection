import sys,os
from pandas import DataFrame
from sensor.exception import SensorException
from sensor.logger import logging
from sensor.entity.config_entity import DataIngestionConfig
from sensor.entity.artifact_entity import DataIngestionArtifact
from sensor.data_access.sensor_data import SensorData


class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig) :
        self.data_ingestion_config = data_ingestion_config

    def export_data_to_feature_store(self) -> DataFrame:
        """
        from mongo db to feature store as csv file
        """
        try:
            logging.info("Exporting data from mongoDB to feature store")
            sensor_data = SensorData()
            dataframe:DataFrame =  sensor_data.export_collection_to_data_frame(collection_name=
            self.data_ingestion_config.collection_name)

            #we now have the dataframe, we will save data in sensor.csv with feature store folder
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path

            #creating folder
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)

            #Saving
            dataframe.to_csv(feature_store_file_path,index=False,header=True)

            return dataframe

        except Exception as e:
            raise SensorException(e,sys)    

    def split_data_train_test(self,dataframe:DataFrame) -> DataFrame:
        """
        Use the feature store data to split into train and test
        """
        try:
            pass
        except Exception as e:
            raise SensorException(e,sys)          

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            dataframe:DataFrame = self.export_data_to_feature_store()
            self.split_data_train_test(dataframe=dataframe)
            data_ingestion_artifact = DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
            test_file_path=self.data_ingestion_config.testing_file_path)

            return data_ingestion_artifact
        except Exception as e:
            raise SensorException(e,sys)  