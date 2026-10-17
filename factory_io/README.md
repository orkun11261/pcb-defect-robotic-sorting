# Factory I/O Digital Twin & 3D Simulation Setup Guide

This guide details the 3D simulation environment created in **Factory I/O** for the **Smart PCB Defect Inspection & Robotic Sorting Cell**.

---

## 1. 3D Scene Overview

The digital twin models an automated industrial electronic manufacturing sorting station consisting of:
- **Primary Transport Line**: Continuous conveyor chain (Entry, Curved, and Exit conveyors) conveying manufactured PCB units.
- **Vision Inspection Zone**: Overhead optical camera mount paired with a precision retroreflective sensor (`First_Detected_Sensor`).
- **Cartesian 3-Axis Pick & Place Gantry**: High-speed gantry equipped with pneumatic Z-axis stroke and industrial vacuum suction cup.
- **Secondary Reject Line**: Perpendicular exit conveyor routing defected boards (`open_circuit`) to the rework bin.
- **Operator Safety Console**: Industrial control panel featuring Start/Stop push buttons and a 3-tier modular Signal Stack Light.

---

## 2. Factory I/O Driver Configuration (Siemens S7-1200)

1. In Factory I/O, open the scene `PCB_Sorting_Cell.factoryio`.
2. Go to **File &rarr; Drivers** and select **Siemens S7-1200/1500** (or **Siemens S7-PLCSIM** if using virtual PLC).
3. Open **Configuration** and set:
   - **Host / IP**: `192.168.0.1` (or your PLC/PLCSIM IP).
   - **Model**: `S7-1200`.
   - **Port**: `102`.
   - **Network Adapter**: Your Ethernet / PROFINET network adapter.
   - **Digital Inputs (Offset)**: `10` (Maps to `%I10.0` - `%I10.5`).
   - **Digital Outputs (Offset)**: `10` (Maps to `%Q10.0` - `%Q11.1`).

---

## 3. Factory I/O & PLC Tag Mapping Table

### Digital Inputs (Sensors to PLC)

| Factory I/O Tag | PLC Address | Type | Physical Function |
| :--- | :--- | :--- | :--- |
| `Start PB` | `%I10.0` | `BOOL` | Green normally open pushbutton on operator console. |
| `Stop PB` | `%I10.1` | `BOOL` | Red normally closed pushbutton on operator console. |
| `Part_At_Inspection` | `%I10.2` | `BOOL` | Retroreflective sensor positioned directly under camera. |
| `Discharge_Sensor` | `%I10.3` | `BOOL` | Diffuse optical sensor at the end of reject conveyor. |
| `Reject_Drop_Sensor`| `%I10.4` | `BOOL` | Optical sensor detecting board placement on reject line. |
| `Grip_Vertical_Limit`| `%I10.5` | `BOOL` | Vertical limit switch confirming vacuum grip contact. |

### Digital Outputs (PLC Actuators)

| Factory I/O Tag | PLC Address | Type | Physical Function |
| :--- | :--- | :--- | :--- |
| `Conveyor Entry (Main)` | `%Q10.0` | `BOOL` | Drives primary entry belt conveyor. |
| `Gantry Move Z` | `%Q10.1` | `BOOL` | Extends pneumatic Z cylinder down to board level. |
| `Vacuum Gripper` | `%Q10.2` | `BOOL` | Engages pneumatic vacuum suction to grasp PCB. |
| `Gantry Move X` | `%Q10.3` | `BOOL` | Translates gantry along X axis to secondary line. |
| `Conveyor Reject` | `%Q10.4` | `BOOL` | Drives secondary defect evacuation conveyor. |
| `Conveyor Curved` | `%Q10.5` | `BOOL` | Drives 90-degree curved transport conveyor. |
| `Conveyor Exit` | `%Q10.6` | `BOOL` | Drives final downstream accepted product conveyor. |
| `Stack Light Red` | `%Q10.7` | `BOOL` | Visual fault indicator (Python disconnected or E-Stop). |
| `Stack Light Green` | `%Q11.0` | `BOOL` | Visual operational indicator (System Run & AI Active). |
| `Stack Light Yellow` | `%Q11.1` | `BOOL` | Visual standby indicator (System Paused & AI Active). |

---

## 4. Testing Procedure with Factory I/O

1. Launch **Siemens TIA Portal** (or S7-PLCSIM) and download the compiled `Main_OB1` and `DB_Python`.
2. Launch **Factory I/O**, load `PCB_Sorting_Cell.factoryio`, and click **Connect** in the Driver tab until a green checkmark appears.
3. Start the Python vision application:
   ```bash
   python src/vision_inspection.py
   ```
4. Press the green **Start Button** (`%I10.0`) on the Factory I/O operator panel.
5. Watch the stack light turn green (`%Q11.0`). As PCBs flow, observe the automated 10-second inspection hold and real-time robotic sorting.
