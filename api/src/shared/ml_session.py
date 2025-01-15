from onnxruntime import InferenceSession
from sklearn.preprocessing import MinMaxScaler


class MLSession:
    """
    A class to represent the machine learning session.

    Attributes:
    - min_max_scalers: The scalers used to preprocess the input data, indexed by feature name
    - ort_session: The ONNX runtime session for the random forest model
    """

    def __init__(
        self, min_max_scalers: dict[str, MinMaxScaler], ort_session: InferenceSession
    ):
        self.min_max_scalers = min_max_scalers
        self.ort_session = ort_session
