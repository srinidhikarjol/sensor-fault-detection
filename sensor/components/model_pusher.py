from sensor.utils.main_utils import load_numpy_array_data
from sensor.exception import SensorException
from sensor.logger import logging
from sensor.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact,DataIngestionArtifact,ModelPusherArtifact,ModelEvaluationArtifact
from sensor.entity.config_entity import ModelPusherConfig
import os,sys
from xgboost import XGBClassifier
import numpy
import shutil
from sensor.ml.model.estimator import SensorModel
from sensor.utils.main_utils import save_object,load_object,write_yaml_file
from sensor.ml.model import estimator
import pandas as pd
from sensor.constant.training_pipeline import TARGET_COLUMN
from sensor.ml.model.estimator import ModelResolver
from sensor.ml.metric.classification_metric import get_classfication_score,ClassficationMetricArtifact

class ModelPusher:

    def __init__(self,
    model_pusher_config:ModelPusherConfig,
    model_eval_artifact:ModelEvaluationArtifact) -> None:
        try:
            self.model_pusher_config = model_pusher_config
            self.model_eval_artifact = model_eval_artifact
        except Exception as e:
            raise SensorException(e,sys)


    def initiate_model_pusher(self) -> ModelPusherArtifact:
        try:
            trained_model_path = self.model_eval_artifact.trained_model_path

            #Creating model pusher dir to save model
            model_file_path = self.model_pusher_config.model_file_path
            os.makedirs(os.path.dirname(model_file_path),exist_ok=True)

            shutil.copy(trained_model_path,model_file_path)

            #saved model dir
            saved_model_path = self.model_pusher_config.saved_model_path
            os.makedirs(os.path.dirname(saved_model_path),exist_ok=True)
            shutil.copy(trained_model_path,saved_model_path)

            model_pusher_artifact = ModelPusherArtifact(
                saved_model_path=saved_model_path,model_file_path=model_file_path
            )

            return model_pusher_artifact
        except Exception as e:
            raise SensorException(e,sys)       