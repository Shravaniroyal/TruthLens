"""
Grad-CAM — spatial attribution for fraud detection.

Hooks the last feature block of EfficientNet-B4, backpropagates the
output logit, and produces a heatmap showing which image regions
influenced the fake/real decision.
"""

from __future__ import annotations

import cv2
import numpy as np
import torch
import torch.nn as nn

from truthlens.config import settings
from truthlens.logging_setup import get_logger

log = get_logger("gradcam")


def compute_gradcam(
    model: nn.Module,
    tensor: torch.Tensor,
    device: torch.device,
) -> tuple[np.ndarray, float]:
    """
    Run forward + backward pass and return (heatmap, fake_probability).

    Args:
        model:  Loaded EfficientNet-B4 in eval mode
        tensor: Preprocessed input [1, 3, H, W]
        device: torch device

    Returns:
        cam: float32 array [H, W] normalized to [0, 1]
        prob: sigmoid probability that document is FAKE
    """
    grads: list[torch.Tensor] = []
    acts: list[torch.Tensor] = []

    def forward_hook(_module, _inputs, output):
        acts.append(output)

    def backward_hook(_module, _grad_input, grad_output):
        grads.append(grad_output[0])

    target_layer = model.features[-1]
    h_fwd = target_layer.register_forward_hook(forward_hook)
    h_bwd = target_layer.register_full_backward_hook(backward_hook)

    try:
        tensor = tensor.to(device).requires_grad_(True)
        output = model(tensor)
        prob = torch.sigmoid(output).item()

        model.zero_grad()
        output.squeeze().backward()

        grad = grads[0].squeeze().cpu().numpy()          # [C, H, W]
        act = acts[0].squeeze().detach().cpu().numpy()  # [C, H, W]
        weights = grad.mean(axis=(1, 2))
        cam = np.maximum((weights[:, None, None] * act).sum(axis=0), 0)
        cam = cv2.resize(cam, (settings.img_size, settings.img_size))
        if cam.max() > 0:
            cam /= cam.max()

        log.debug("Grad-CAM computed | fake_prob=%.4f | cam_max=%.4f", prob, cam.max())
        return cam.astype(np.float32), prob

    finally:
        h_fwd.remove()
        h_bwd.remove()
        model.zero_grad(set_to_none=True)
