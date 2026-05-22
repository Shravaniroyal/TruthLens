import torch
import torch.nn as nn
import numpy as np
import cv2
import timm
from PIL import Image
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os

# ── CONFIG ──────────────────────────────────────────────────
MODEL_PATH = r'C:\Users\Shravani\TruthLens\models\best_truthlens_v3.pth'
DEVICE     = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ── LOAD MODEL ──────────────────────────────────────────────
def load_model():
    model = timm.create_model('efficientnet_b4', pretrained=False, num_classes=2)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    model.to(DEVICE)
    return model

# ── GRAD-CAM CLASS ──────────────────────────────────────────
class GradCAM:
    def __init__(self, model):
        self.model     = model
        self.gradients = None
        self.activations= None

        # EfficientNet-B4 target layer
        target_layer = model.blocks[-1]
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, input_tensor, class_idx=None):
        self.model.zero_grad()
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = output.argmax(dim=1).item()

        score = output[0, class_idx]
        score.backward()

        # Compute CAM
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam     = (weights * self.activations).sum(dim=1, keepdim=True)
        cam     = torch.relu(cam)
        cam     = cam.squeeze().cpu().numpy()

        # Normalize
        cam = cv2.resize(cam, (224, 224))
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam, class_idx, output.softmax(dim=1)[0].detach().cpu().numpy()

# ── PREDICT + VISUALIZE ─────────────────────────────────────
def analyze_document(image_path, output_path=None):
    model  = load_model()
    gradcam= GradCAM(model)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    # Load image
    img_pil  = Image.open(image_path).convert('RGB')
    img_tensor = transform(img_pil).unsqueeze(0).to(DEVICE)
    img_tensor.requires_grad_()

    # Generate CAM
    cam, pred_class, probs = gradcam.generate(img_tensor)

    # Labels: 0=real, 1=fake
    label      = 'FAKE / TAMPERED' if pred_class == 1 else 'AUTHENTIC'
    confidence = probs[pred_class] * 100
    color      = (0, 0, 255) if pred_class == 1 else (0, 200, 0)

    # Create heatmap overlay
    img_np  = np.array(img_pil.resize((224, 224)))
    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    overlay = cv2.addWeighted(img_np, 0.6, heatmap, 0.4, 0)

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor('white')

    axes[0].imshow(img_np)
    axes[0].set_title('Original Document', fontsize=13, fontweight='bold')
    axes[0].axis('off')

    axes[1].imshow(heatmap)
    axes[1].set_title('Fraud Heatmap\n(Red = Suspicious Region)', fontsize=13, fontweight='bold')
    axes[1].axis('off')

    axes[2].imshow(overlay)
    title_color = 'red' if pred_class == 1 else 'green'
    axes[2].set_title(f'TruthLens Verdict\n{label} ({confidence:.1f}%)',
                      fontsize=13, fontweight='bold', color=title_color)
    axes[2].axis('off')

    plt.suptitle('TruthLens — AI Document Fraud Detection',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()

    # Save
    if output_path is None:
        base = os.path.splitext(image_path)[0]
        output_path = base + '_gradcam.png'

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Verdict    : {label}")
    print(f"Confidence : {confidence:.1f}%")
    print(f"Real prob  : {probs[0]*100:.1f}%")
    print(f"Fake prob  : {probs[1]*100:.1f}%")
    print(f"Saved to   : {output_path}")
    return label, confidence, output_path

# ── MAIN — test on a sample image ───────────────────────────
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default: find any image in your dataset to test with
        test_dirs = [
            r'C:\Users\Shravani\TruthLens\final_dataset_v3_fixed\test\fake',
            r'C:\Users\Shravani\TruthLens\final_dataset_v3_fixed\test\real',
            r'C:\Users\Shravani\TruthLens\industry_datasets\fake_documents',
        ]
        image_path = None
        for d in test_dirs:
            if os.path.exists(d):
                files = [f for f in os.listdir(d)
                         if f.lower().endswith(('.jpg','.jpeg','.png','.tif','.tiff'))]
                if files:
                    image_path = os.path.join(d, files[0])
                    break

    if image_path:
        print(f"Analyzing: {image_path}")
        analyze_document(image_path)
    else:
        print("No image found. Run: python gradcam_truthlens.py path\\to\\image.jpg")