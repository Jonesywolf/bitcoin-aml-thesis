from sklearn.preprocessing import MinMaxScaler
from onnxruntime import InferenceSession
import numpy as np

from src.shared.ml_session import MLSession
from src.models import WalletData


def classify_wallet(ort_session: InferenceSession, wallet_data: np.ndarray) -> int:
    """
    Classify a wallet using the random forest model.

    Parameters:
    - ort_session: The ONNX runtime session for the random forest model
    - wallet_data: The wallet data to classify as a numpy array

    Returns:
    - The classification result (licit: 0 or illicit: 1)
    """
    # Prepare the input data
    input_data = wallet_data.astype(np.float32).reshape(1, -1)

    # Run the model
    outputs = ort_session.run(None, {"float_input": input_data})

    return int(outputs[0][0])


def infer_wallet_data_class(
    ml_session: MLSession, wallet_data: WalletData
) -> WalletData:
    """
    Classify a wallet using the random forest model.

    Parameters:
    - ml_session: The min max scalers and the ONNX runtime session for the random forest model
    - wallet_data: The wallet data to classify

    Returns:
    - The wallet data with the class inference set
    """

    new_wallet_data = wallet_data.model_copy()
    wallet_data_values = wallet_data.to_ml_model_input(ml_session.min_max_scalers)
    new_wallet_data.class_inference = classify_wallet(
        ml_session.ort_session, wallet_data_values
    )

    return new_wallet_data
