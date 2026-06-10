# utils/label_decoder.py
import pickle
from config import ENCODER_PATH

class LabelDecoder:
    def __init__(self):
        with open(ENCODER_PATH, "rb") as f:
            self.encoder = pickle.load(f)

    def decode(self, class_id: int) -> str:
        return self.encoder.inverse_transform([class_id])[0]

    @property
    def classes(self):
        return list(self.encoder.classes_)