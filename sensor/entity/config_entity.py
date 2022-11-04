from datetime import date, datetime
import os,sys
from sensor.exception import SensorException
from sensor.constant import training_pipeline

"""
An object of TrainingPipelineConfig would have the path to artifact->timestamp
which is common to all the configs. This object will be passed as a parameter
to other configurations.
"""
class TrainingPipelineConfig:

    def __init__(self,timestamp=datetime.now()):
        timestamp = timestamp.strftime("%m_%d_%Y_%H_%M_%S")
        #self.pipeline_name = training_pipeline.PIPELINE_NAME
        self.artifact_dir_name = os.path.join(training_pipeline.ARTIFACT_DIR, timestamp)
        self.timestamp = timestamp


class DataIngestionConfig:

    def __init__(self,training_pipeline_config:TrainingPipelineConfig) :
        self.data_ingestion_dir:str = os.path.join(
            training_pipeline_config.artifact_dir_name,training_pipeline.DATA_INGESTION_DIR_NAME)

        self.feature_store_file_path:str = os.path.join(
          self.data_ingestion_dir,training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR,training_pipeline.FILE_NAME)

        self.training_file_path:str = os.path.join(
        self.data_ingestion_dir,training_pipeline.DATA_INGESTION_INGESTED_DIR,training_pipeline.TRAIN_FILE_NAME)      

        self.testing_file_path:str = os.path.join(
        self.data_ingestion_dir,training_pipeline.DATA_INGESTION_INGESTED_DIR,training_pipeline.TEST_FILE_NAME)

        self.train_test_split_ratio: float = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATION
        self.collection_name: str = training_pipeline.DATA_INGESTION_COLLECTION_NAME    
          

class DataValidationConfig:

    def __init__(self,training_pipeline_config:TrainingPipelineConfig) -> None:
        try:
            self.data_validation_dir: str = os.path.join( training_pipeline_config.artifact_dir_name, training_pipeline.DATA_VALIDATION_DIR_NAME)
            self.valid_data_dir: str = os.path.join(self.data_validation_dir, training_pipeline.DATA_VALIDATION_VALID_DIR)
            self.invalid_data_dir: str = os.path.join(self.data_validation_dir, training_pipeline.DATA_VALIDATION_INVALID_DIR)
            self.valid_train_file_path: str = os.path.join(self.valid_data_dir, training_pipeline.TRAIN_FILE_NAME)
            self.valid_test_file_path: str = os.path.join(self.valid_data_dir, training_pipeline.TEST_FILE_NAME)
            self.invalid_train_file_path: str = os.path.join(self.invalid_data_dir, training_pipeline.TRAIN_FILE_NAME)
            self.invalid_test_file_path: str = os.path.join(self.invalid_data_dir, training_pipeline.TEST_FILE_NAME)
            self.drift_report_file_path: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_DIR,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME,
        )

        except Exception as e:
            raise SensorException(e,sys)