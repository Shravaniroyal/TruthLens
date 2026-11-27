"""
EfficientNet-B4 model — build, load, and cache.

Architecture matches v4 training:
  Dropout(0.4) → Linear(1792→512) → ReLU → Dropout(0.3) → Linear(512→1)

Output is a single logit; apply sigmoid for fake probability.
"""

from __future__ import annotations

from functools import lru_cache

import torch
import torch.nn as nn
import torchvision.models as tv_models

from truthlens.config import settings
from truthlens.exceptions import ModelLoadError
from truthlens.logging_setup import get_logger

log = get_logger("model")


def _load_checkpoint(model_path, device):
    """Load a .pth file. Prefer weights_only=True; fall back for older PyTorch or extra metadata."""
    try:
        return torch.load(model_path, map_location=device, weights_only=True)
    except TypeError:
        return torch.load(model_path, map_location=device)
    except Exception:
        log.warning("weights_only=True failed; retrying full unpickle of checkpoint")
        return torch.load(model_path, map_location=device)


def get_device() -> torch.device:
    """Select CUDA when available, otherwise CPU."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info("Compute device: %s", device)
    return device


def build_model() -> nn.Module:
    """Construct EfficientNet-B4 with the v4 classification head."""
    model = tv_models.efficientnet_b4(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(512, 1),
    )
    return model


@lru_cache(maxsize=1)
def load_model() -> tuple[nn.Module, torch.device]:
    """
    Load model weights once and cache in-process.
    Returns (model, device). Raises ModelLoadError on failure.
    """
    model_path = settings.model_path
    device = get_device()

    if not model_path.exists():
        log.error("Model file not found: %s", model_path)
        raise ModelLoadError(f"Model not found at {model_path}")

    log.info("Loading model weights from %s", model_path)
    try:
        model = build_model()
        raw_state = _load_checkpoint(model_path, device)
        if not isinstance(raw_state, dict):
            raise ModelLoadError("Checkpoint is not a state dictionary")
        if "state_dict" in raw_state:
            raw_state = raw_state["state_dict"]
        # Strip DataParallel 'module.' prefix if checkpoint was saved on multi-GPU
        state = {k.replace("module.", ""): v for k, v in raw_state.items()}
        model.load_state_dict(state)
        model.eval()
        model.to(device)
        log.info("Model loaded successfully | version=%s", settings.model_version)
        return model, device
    except Exception as exc:
        log.exception("Failed to load model")
        raise ModelLoadError(str(exc)) from exc
