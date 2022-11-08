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
        preproces_x = self.preprocessor(x)
        y_val = self.model.predict(preproces_x)
        return y_val            