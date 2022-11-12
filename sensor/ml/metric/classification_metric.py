from sensor.entity.artifact_entity import ClassficationMetricArtifact
from sensor.exception import SensorException
from sklearn.metrics import f1_score,precision_score,recall_score
import sys

def get_classfication_score(y_true,y_pred) -> ClassficationMetricArtifact:
    try:
        model_f1_score = f1_score(y_true,y_pred)
        model_recall_score = recall_score(y_true,y_pred)
        model_precision_score = precision_score(y_pred,y_pred)

        classfication_metric_artifact: ClassficationMetricArtifact = ClassficationMetricArtifact(f1_score=model_f1_score,precision_score=model_precision_score,
        recall_scroe=model_recall_score)

        return classfication_metric_artifact
    except Exception as e:
        raise SensorException(e,sys)          
