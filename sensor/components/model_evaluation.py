from sensor.utils.main_utils import load_numpy_array_data
from sensor.exception import SensorException
from sensor.logger import logging
from sensor.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact,DataIngestionArtifact,DataValidationArtifact,ModelEvaluationArtifact
from sensor.entity.config_entity import ModelEvaluationConfig
import os,sys
from xgboost import XGBClassifier
import numpy
from sensor.ml.model.estimator import SensorModel
from sensor.utils.main_utils import save_object,load_object,write_yaml_file
from sensor.ml.model import estimator
import pandas as pd
from sensor.constant.training_pipeline import TARGET_COLUMN
from sensor.ml.model.estimator import ModelResolver,TargetValueMapping
from sensor.ml.metric.classification_metric import get_classfication_score,ClassficationMetricArtifact

class ModelEvaluation:

    def __init__(self,model_eval_config: ModelEvaluationConfig,
    data_validation_artifact:DataValidationArtifact,model_trainer_artifact:ModelTrainerArtifact) -> None:
        try:
            self.model_eval_config = model_eval_config
            self.data_validation_artifact = data_validation_artifact
            self.model_trainer_artifact = model_trainer_artifact
        except Exception as e:
            raise SensorException(e,sys)


    def initialize_model_evaluation(self) -> ModelEvaluationArtifact:
        try:
            valid_train_file_path = self.data_validation_artifact.valid_train_file_path
            valid_test_file_path = self.data_validation_artifact.valid_test_file_path

            train_df = pd.read_csv(valid_train_file_path)
            test_df = pd.read_csv(valid_test_file_path)

            train_model_file_path = self.model_trainer_artifact.trained_model_file_path

            model_resolver = ModelResolver()

            #Check if there exists a best model in "saved_models"
            #If not, make the current trained model as best model
            if not model_resolver.is_model_exists():
                model_evaluation_artifact = ModelEvaluationArtifact(
                    is_model_accepted=True,
                    improved_accuracy=None,
                    best_model_path=None,
                    trained_model_path=train_model_file_path,
                    train_model_metric_artifact=self.model_trainer_artifact.train_metric_artifact,
                    best_model_metric_artifact=None
                )
                return model_evaluation_artifact

            latest_model_path = model_resolver.get_best_model_path()
            
            #loading train and best models
            latest_model = load_object(file_path=latest_model_path)
            train_model = load_object(file_path=train_model_file_path)

            merge_df = pd.concat([train_df,test_df])
            y_true = merge_df[TARGET_COLUMN]
            y_true.replace(TargetValueMapping().to_dict(),inplace=True)
            merge_df.drop(TARGET_COLUMN,axis=1,inplace=True)
            #predictions
            y_train_pred = train_model.predict(merge_df)
            y_latest_pred = latest_model.predict(merge_df)

            #Get the  classification scores
            train_metric: ClassficationMetricArtifact = get_classfication_score(y_true=
            y_true,y_pred=y_train_pred)
            
            latest_metric: ClassficationMetricArtifact = get_classfication_score(y_true=
            y_true,y_pred=y_latest_pred)

            if train_metric.f1_score - latest_metric.f1_score > self.model_eval_config.change_threshold:
                is_model_accepted = True
            else:
                is_model_accepted = False

            model_evaluation_artifact = ModelEvaluationArtifact(
                    is_model_accepted=is_model_accepted,
                    improved_accuracy=train_metric.f1_score-latest_metric.f1_score,
                    best_model_path=latest_model_path,
                    trained_model_path=train_model_file_path,
                    train_model_metric_artifact=train_metric,
                    best_model_metric_artifact=latest_metric
            )

            model_eval_report = model_evaluation_artifact.__dict__
            write_yaml_file(self.model_eval_config.report_file_path,model_eval_report)
            return model_evaluation_artifact
            

        except Exception as e:
            raise SensorException(e,sys) 
            