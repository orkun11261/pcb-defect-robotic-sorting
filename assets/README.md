# Repository Visual Assets & Architecture Schematics

This directory contains visual documentation assets, interactive architecture schematics, and simulation screencasts for the **Smart PCB Defect Inspection & Robotic Sorting Cell**.

---

## Asset Catalog

| Asset Filename | Format | Description |
| :--- | :--- | :--- |
| **`system_architecture.svg`** | SVG (Vector) | Comprehensive industrial architecture: S7-1200, Factory I/O, Snap7, YOLOv8, and DB1 memory map. |
| **`state_machine.svg`** | SVG (Vector) | State transition diagram: Optical detection, 10s dynamic window, robotic Pick & Place, and pass/fail routing. |
| **`demo_sorting_cell.gif`** | GIF / MP4 | High-resolution screencast demonstrating real-time Factory I/O 3D simulation with Python HUD overlay. |
| **`plc_ladder_diagrams/`** | PNG / PDF | High-definition graphical exports of TIA Portal OB1 Networks 2 through 10. |

---

## Recommended Dimensions for Visuals
- Architecture Diagrams: 1920x1080 (16:9), transparent background or industrial dark theme.
- Video GIF: 1280x720, 24-30 FPS, optimized via `ffmpeg` / `gifsicle` to stay under 15 MB.
