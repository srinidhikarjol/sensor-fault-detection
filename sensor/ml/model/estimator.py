from sensor.exception import SensorException
import sys,os
from sensor.constant.training_pipeline import SAVED_MODEL_DIR,MODEL_FILE_NAME
class TargetValueMapping:
    def __init__(self):
        self.neg: int = 0
        self.pos: int = 1

    def to_dict(self):
        return self.__dict__

    def reverse_mapping(self):
        mapping_response = self.to_dict()
        return dict(zip(mapping_response.values(),mapping_response.keys()))    


class SensorModel:

    def __init__(self,preprocessor,model) -> None:
        self.preprocessor = preprocessor
        self.model = model

    def predict(self,x):
        preproces_x = self.preprocessor.transform(x)
        y_val = self.model.predict(preproces_x)
        return y_val            

class ModelResolver:

    def __init__(self,model_dir=SAVED_MODEL_DIR) -> None:
        #Note - in this folder we will be having models based on timestamp
        self.model_dir = model_dir


    def get_best_model_path(self) -> str:
        try:
            timestamps = list(map(int,os.listdir(self.model_dir)))
            latest_timsestamp = max(timestamps)
            latest_model_file_path = os.path.join(self.model_dir,
            f"{latest_timsestamp}",MODEL_FILE_NAME)
            return latest_model_file_path

        except Exception as e:
            raise SensorException(e,sys)

    def is_model_exists(self) -> bool:
        try:
            #check if "saved_models" directory exisits
            if not os.path.exists(self.model_dir):
                return False

            #check if the "saved_models" directory is empty    
            timestamps = os.listdir(self.model_dir)
            if len(timestamps) == 0:
                return False

            latest_model_path = self.get_best_model_path()
            #check if there exists a latest model
            if not os.path.exists(latest_model_path):
                return False 

            return True       

        except Exception as e:
            raise SensorException(e,sys)    