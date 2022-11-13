import sys
from sympy import EX
from sensor.entity.config_entity import TrainingPipelineConfig,DataIngestionConfig,DataValidationConfig,DataTransformationConfig,ModelEvaluationConfig,ModelPusherConfig,ModelTrainerConfig
from sensor.exception import SensorException
import sys,os
from sensor.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact,ModelEvaluationArtifact,ModelPusherArtifact,ModelTrainerArtifact
from sensor.logger import logging
from sensor.components.data_ingestion import DataIngestion
from sensor.components.data_validation import DataValidation
from sensor.components.data_transformation import DataTransformation
from sensor.components.model_evaluation import ModelEvaluation
from sensor.components.model_trainer import ModelTrainer
from sensor.components.model_pusher import ModelPusher
from sensor.cloud_storage.s3_syncer import S3Sync
from sensor.constant.s3_bucket import TRAINING_BUCKET_NAME
from sensor.constant.training_pipeline import SAVED_MODEL_DIR


class TrainPipeline:
    def __init__(self) :
        self.training_pipeline_config = TrainingPipelineConfig()
        self.is_pipeline_running = False

    def start_data_ingestion(self) -> DataIngestionArtifact :
        try:
        
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=
            self.training_pipeline_config)
            logging.info("Starting data ingestion")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info("Data ingestion complete")

            return data_ingestion_artifact
        except Exception as e:
            raise SensorException(e,sys) 
            
    def start_data_validation(self,data_ingestion_artifact:DataIngestionArtifact) -> DataValidationArtifact:
        try:
            self.data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting data validation")
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,data_validation_config=self.data_validation_config)
            data_validation_artifact:DataValidationArtifact = data_validation.initiate_data_validation()
            logging.info("Data Validation complete")
            return data_validation_artifact
        except Exception as e:
            raise SensorException(e,sys) 

    def start_data_transformation(self,data_validation_artifact:DataValidationArtifact):
        try:
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting data transformation")
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,data_transformation_config=data_transformation_config)
            data_transformation_artifact:DataTransformationArtifact = data_transformation.initiate_data_transformation()
            logging.info("Data Transformation complete")
            return data_transformation_artifact
        except Exception as e:
            raise SensorException(e,sys) 

    def start_model_trainer(self,
    data_transformation_artifact:DataTransformationArtifact):
        try:
            model_trainer_config = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            model_trainer = ModelTrainer(model_trainer_config=model_trainer_config,data_transform_artifact=data_transformation_artifact)
            model_trainer_artifact: ModelTrainerArtifact = model_trainer.initiate_model_trainer()
            return model_trainer_artifact
        except Exception as e:
            raise SensorException(e,sys)                          

    def start_model_evaluation(self,
    data_validation_artifact:DataValidationArtifact,model_trainer_artifact:ModelTrainerArtifact):
        try:
           model_eval_config = ModelEvaluationConfig(self.training_pipeline_config)
           model_eval = ModelEvaluation(model_eval_config=model_eval_config,
           data_validation_artifact=data_validation_artifact,
           model_trainer_artifact=model_trainer_artifact)

           model_eval_artifact = model_eval.initialize_model_evaluation() 
           return model_eval_artifact 
        except Exception as e:
            raise SensorException(e,sys)  

    def start_model_pusher(self,model_eval_artifact:ModelEvaluationArtifact):
        try:
            model_pusher_config = ModelPusherConfig(training_pipeline_config=self.training_pipeline_config)
            model_pusher = ModelPusher(model_pusher_config=model_pusher_config,model_eval_artifact=model_eval_artifact)
            model_pusher_artifact:ModelPusherArtifact =  model_pusher.initiate_model_pusher()
            return model_pusher_artifact
        except Exception as e:
            raise SensorException(e,sys)  

    def sync_artifact_dir_to_s3(self):
        try:
            #we are syncing the artifact directory
            #everytime we run the pipeline, the pipeline will run,
            #gothrough the process and the artifact directory and model are uploaded onto S3
            aws_buket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.artifact_dir,aws_buket_url=aws_buket_url)
        except Exception as e:
            raise SensorException(e,sys)
            
    def sync_saved_model_dir_to_s3(self):
        try:
            #we are syncing the trained model
            aws_buket_url = f"s3://{TRAINING_BUCKET_NAME}/{SAVED_MODEL_DIR}"
            self.s3_sync.sync_folder_to_s3(folder = SAVED_MODEL_DIR,aws_buket_url=aws_buket_url)
        except Exception as e:
            raise SensorException(e,sys)                 

    def run_pipeline(self):
        try:
            self.is_pipeline_running = True
            data_ingestion_artifact:  DataIngestionArtifact = self.start_data_ingestion()
            data_validation_artifact: DataValidationArtifact= self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact: DataTransformationArtifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact : ModelTrainerArtifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            model_eval_artifact: ModelEvaluationArtifact = self.start_model_evaluation(data_validation_artifact,model_trainer_artifact)
            if not model_eval_artifact.is_model_accepted:
                raise Exception("Trained model is not better than the best model saved!")
            model_pusher_artifact = self.start_model_pusher(model_eval_artifact=model_eval_artifact)   
            self.is_pipeline_running = False 
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()
        except Exception as e:
            self.sync_artifact_dir_to_s3()
            self.is_pipeline_running = False
            raise SensorException(e,sys)       