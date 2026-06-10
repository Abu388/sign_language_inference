# inference.py
import torch
import torch.nn as nn
import numpy as np
import logging
from config import (MODEL_PATH, SEQUENCE_LENGTH, INPUT_DIM, D_MODEL,
                    N_HEAD, N_LAYERS, DIM_FF, DROPOUT, DEVICE)
from utils.keypoint_extractor import extract_keypoints_from_video
from utils.normalizer import KeypointNormalizer
from utils.label_decoder import LabelDecoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 100, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(max_len).unsqueeze(1).float()
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))  # (1, max_len, d_model)

    def forward(self, x):
        # x: (batch, seq, d_model)
        return self.dropout(x + self.pe[:, :x.size(1)])

class SignModel(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()
        self.input_proj = nn.Sequential(
            nn.Linear(INPUT_DIM, D_MODEL),
            nn.LayerNorm(D_MODEL)
        )
        self.pos_enc = PositionalEncoding(D_MODEL, dropout=DROPOUT)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=D_MODEL,
            nhead=N_HEAD,
            dim_feedforward=DIM_FF,
            dropout=DROPOUT,
            batch_first=True,      # Must match training
            norm_first=True,
            activation="gelu"
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=N_LAYERS)
        self.head = nn.Sequential(
            nn.LayerNorm(D_MODEL),
            nn.Dropout(DROPOUT),
            nn.Linear(D_MODEL, num_classes)
        )

    def forward(self, x):
        # x shape: (batch, seq, INPUT_DIM)
        logger.debug(f"Input to SignModel: {x.shape}")
        x = self.input_proj(x)            # (batch, seq, D_MODEL)
        logger.debug(f"After input_proj: {x.shape}")
        x = self.pos_enc(x)               # (batch, seq, D_MODEL)
        logger.debug(f"After pos_enc: {x.shape}")
        x = self.transformer(x)           # (batch, seq, D_MODEL)
        logger.debug(f"After transformer: {x.shape}")
        x = x.mean(dim=1)                 # (batch, D_MODEL)
        logger.debug(f"After mean: {x.shape}")
        return self.head(x)               # (batch, num_classes)

class SignLanguageInference:
    def __init__(self, debug_shapes=False):
        if debug_shapes:
            logging.getLogger().setLevel(logging.DEBUG)
        self.label_decoder = LabelDecoder()
        num_classes = len(self.label_decoder.classes)
        self.model = SignModel(num_classes=num_classes).to(DEVICE)
        # Load weights
        state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.normalizer = KeypointNormalizer()

    def _ensure_3d(self, tensor):
        """Convert any tensor to (batch, seq, features)."""
        if tensor.dim() == 2:
            return tensor.unsqueeze(0)   # (seq, features) -> (1, seq, features)
        elif tensor.dim() == 3:
            return tensor
        elif tensor.dim() == 4:
            # If extra dimension of size 1, squeeze it
            if tensor.size(0) == 1 and tensor.size(3) == 1:
                logger.warning(f"Squeezing 4D tensor of shape {tensor.shape} to 3D")
                return tensor.squeeze(0).squeeze(-1)
            else:
                raise ValueError(f"Cannot automatically fix 4D tensor shape {tensor.shape}. "
                                 f"Expected (batch, seq, features).")
        else:
            raise ValueError(f"Unsupported tensor dimension: {tensor.dim()}")

    def predict_video(self, video_path: str):
        # 1. Extract keypoints
        keypoints = extract_keypoints_from_video(video_path)
        if keypoints is None:
            raise ValueError(f"Failed to extract keypoints from {video_path}")
        logger.debug(f"Keypoints shape (after extraction): {keypoints.shape}")

        # 2. Normalize
        keypoints_norm = self.normalizer(keypoints)
        logger.debug(f"Keypoints shape (after norm): {keypoints_norm.shape}")

        # 3. Convert to tensor and ensure 3D
        input_tensor = torch.from_numpy(keypoints_norm).float()
        input_tensor = self._ensure_3d(input_tensor).to(DEVICE)
        logger.debug(f"Final input tensor shape: {input_tensor.shape}")

        # 4. Inference
        with torch.no_grad():
            logits = self.model(input_tensor)
            probs = torch.softmax(logits, dim=1)
            pred_id = torch.argmax(probs, dim=1).item()
            confidence = probs[0, pred_id].item()

        class_name = self.label_decoder.decode(pred_id)
        logger.info(f"Prediction: {class_name} (confidence={confidence:.3f})")
        return class_name, confidence