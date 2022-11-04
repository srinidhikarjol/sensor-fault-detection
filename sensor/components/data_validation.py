from sensor.entity.config_entity import DataValidationConfig
from sensor.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
import pandas as pd
import os,sys
from sensor.exception import SensorException
from sensor.constant.training_pipeline import SCHEMA_FILE_PATH
from sensor.utils.main_utils import read_yaml_file
from sensor.utils.main_utils import write_yaml_file
from sensor.logger import logging
from scipy.stats import ks_2samp

class DataValidation:
    
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
    data_validation_config:DataValidationConfig) -> None:
        self.data_ingestion_artifact = data_ingestion_artifact
        self.data_validation_config = data_validation_config
        self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)

    def validate_number_of_columns(self,dataframe:pd.DataFrame) -> bool:
        try:
           no_of_cols =  self._schema_config['columns']
           if len(no_of_cols) == len(dataframe.columns):
            return True
           else:
            return False 

        except Exception as e:
            raise SensorException(e,sys)

    def is_numerical_column_exist(self,dataframe:pd.DataFrame) -> bool:
        try:
            no_of_numerical_cols =  self._schema_config['numerical_columns']
            dataframe_columns = dataframe.columns
            all_equal = True
            missing_cols = []
            for num_column in no_of_numerical_cols:
                if num_column not in dataframe_columns:
                    all_equal = False
                    missing_cols.append(num_column)

            logging.info(f"Missing numerical columns: [{missing_cols}]")
            return all_equal

        except Exception as e:
            raise SensorException(e,sys)


    def drop_zero_std_columns(self,dataframe):
        pass        

    @staticmethod    
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise SensorException(e,sys)


    def get_drift_report(self,base_df:pd.DataFrame,current_df:pd.DataFrame,threshold=0.05) -> bool:
        try:
            report = {}
            drift_found = False
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]  
                has_same_dist = ks_2samp(d1,d2)
                if threshold <= has_same_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    drift_found = True
                report.update({column:{
                        "p_value":float(has_same_dist.pvalue),
                        "drift_status":is_found
                    }})     

            drift_report_file_path = self.data_validation_config.drift_report_file_path  
            dir_path = os.path.dirname(drift_report_file_path)
            write_yaml_file(file_path=drift_report_file_path,content=report)          

            return drift_found  
        except Exception as e:
            raise SensorException(e,sys)             
            
    def detect_dataset_drift(self):
        pass

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            error_message = ""
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path  = self.data_ingestion_artifact.test_file_path

            #Reading data from train and test
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe  = DataValidation.read_data(test_file_path)

            #Validating number of columns
            status = self.validate_number_of_columns(dataframe=train_dataframe)
            if not status:
                error_message = f"{error_message}Train dataframe does not contain all columns."

            status = self.validate_number_of_columns(dataframe=test_dataframe)
            if not status:
                error_message = f"{error_message}Test dataframe does not contain all columns."    

            #Validate if numerical columns exist
            status = self.is_numerical_column_exist(dataframe=train_dataframe)
            if not status:
                error_message = f"{error_message}Train dataframe does not contain all numerical columns."
            status = self.is_numerical_column_exist(dataframe=test_dataframe)
            if not status:
                error_message = f"{error_message}Train dataframe does not contain all numerical columns."

            if len(error_message) > 0:
                raise Exception(error_message)

            #Lets check data drift
            # evidentlyai -> library    
            is_drift_found:bool =  self.get_drift_report(base_df=train_dataframe,current_df=test_dataframe)  

            data_validation_artifact = DataValidationArtifact(
                validation_status=is_drift_found,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )

            logging.info(f"Data validation artifact: {data_validation_artifact}")

            return data_validation_artifact

        except Exception as e:
            raise SensorException(e,sys)