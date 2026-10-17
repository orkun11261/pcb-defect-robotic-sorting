# Custom YOLOv8 PCB Defect Detection Model (`pcb_model_V2.pt`)

This directory houses the deep learning model inference configuration, target defect class definitions, and weights placement instructions for real-time PCB defect identification.

---

## 🔗 Model Training & Dataset Repository

> [!TIP]
> The full dataset preparation, image annotation, augmentations, loss graphs, hyperparameter sweeps, and training pipeline for `pcb_model_V2.pt` are maintained in the dedicated repository:
> 
> 👉 **[GitHub: orkun11261/pcb-copper-trace-inspection](https://github.com/orkun11261/pcb-copper-trace-inspection)**

Please refer to that repository for:
- Detailed dataset collection and optical microscopy procedures.
- Synthetic & real PCB defect augmentations.
- Weights & Biases (W&B) experiment logs and training curves.
- Export pipelines for ONNX, OpenVINO, and TensorRT engines.

---

## 1. Target Defect Classes

The production model `pcb_model_V2.pt` detects the following surface and trace defects:

| Class ID | Class Label | Defect Category | Industrial Impact |
| :---: | :--- | :--- | :--- |
| `0` | **`open_circuit`** | Discontinuous copper trace | Critical electrical discontinuity, complete PCB failure. |
| `1` | **`short_circuit`** | Accidental copper bridge | Pin-to-pin or trace-to-trace short circuit. |
| `2` | **`missing_component`** | Absent SMD component | Inoperable circuit subsystem. |
| `3` | **`solder_bridge`** | Solder shorting IC pads | High failure risk during automated testing. |
| `4` | **`spur`** | Trace margin copper burr | High-voltage dielectric breakdown risk. |

---

## 2. Real-Time Inference Latency Benchmarks

| Compute Device | Precision | Inference Time (ms) | Equivalent Camera FPS |
| :--- | :---: | :---: | :---: |
| **NVIDIA RTX 4090 (TensorRT)** | FP16 | **4.2 ms** | ~238 FPS |
| **NVIDIA RTX 3080 (PyTorch)** | FP16 | **11.8 ms** | ~84 FPS |
| **NVIDIA GTX 1660 Ti** | FP32 | **24.5 ms** | ~40 FPS |
| **Intel Core i7-13700K (CPU)** | FP32 | **48.0 ms** | ~20 FPS |

*Note: Because inference runs asynchronously in a dedicated worker thread ([`src/vision_inspection.py`](file:///c:/Users/orkunarda/Desktop/Linkedin/Python_PLC/src/vision_inspection.py)), the live OpenCV display loop maintains steady 30-60 FPS even when running on CPU.*

---

## 3. Acquiring Model Weights

Place your trained `pcb_model_V2.pt` weights file directly into this directory:
```bash
# Directory: models/
pcb_model_V2.pt
```
For simulation/testing without weights, start the inspection runner with:
```bash
python src/vision_inspection.py --mock
```
