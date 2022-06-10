from abc import ABC
import json


def loadModel(jsonModel):
    try:
        return json.loads(jsonModel)
    except Exception as e:
        print(e)
    return jsonModel


class JSONSerializator(ABC):

    def serialize(self, jsonModel, ignoreProperties=True):
        model = loadModel(jsonModel)
        keys = model.keys()
        for key in keys:
            if ignoreProperties is True:
                setattr(self, key, model.get(key))
            else:
                if hasattr(self, key):
                    setattr(self, key, model.get(key))
        return self

    def dumpModel(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)