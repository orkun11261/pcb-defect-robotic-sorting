# Siemens S7-1200 PLC Architecture & LADDER Logic Documentation

This directory contains the industrial automation logic, tag definitions, and memory mappings for the **Smart PCB Defect Inspection & Robotic Sorting Cell** developed using **Siemens TIA Portal V18** and **LADDER / SCL** programming.

---

## 1. Hardware & Software Specifications

- **Controller**: Siemens SIMATIC S7-1200 (CPU 1214C DC/DC/DC or CPU 1215C DC/DC/DC).
- **Firmware**: V4.4 / V4.5+.
- **Engineering Suite**: Siemens TIA Portal V18.
- **Protocol**: Siemens S7 Communication (Native RFC1006 / ISO-on-TCP, Port 102).
- **Execution Cycle**: Main Cyclic Organization Block (`OB1`).

---

## 2. Mandatory TIA Portal V18 Configuration Rules

For `python-snap7` to read and write DB bits in real-time, the following two security and compiler settings **MUST** be applied in TIA Portal V18:

1. **Permit PUT/GET Access**:
   - Navigate to `PLC Properties` -> `Protection & Security` -> `Connection Mechanisms`.
   - Check the box: **"Permit access with PUT/GET communication from remote partner"**.
2. **Disable Optimized Block Access on DB1**:
   - Right-click `DB1 ("DB_Python")` -> `Properties` -> `Attributes`.
   - **Uncheck** "Optimized block access".
   - This enforces standard byte-aligned offset addressing (`DB1.DBX0.0`, `DB1.DBX0.1`, `DB1.DBX0.2`).

---

## 3. Data Block 1 (`DB_Python`) Memory Map

| Symbol | Address | Data Type | Direction | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`Trigger`** | `DB1.DBX0.0` | `BOOL` | Python &rarr; PLC | High pulse written by Python when a PCB defect (`open_circuit`) is detected. Sets sorting memory. |
| **`Part_At_Camera`** | `DB1.DBX0.1` | `BOOL` | PLC &rarr; Python | Set to 1 when a PCB reaches `First_Detected_Sensor` (%I10.2). Triggers the 10s inspection window. |
| **`Heartbeat`** | `DB1.DBX0.2` | `BOOL` | Python &rarr; PLC | Life pulse periodically sent by Python to service the hardware Watchdog timer (`TOF 1.0s`). |

---

## 4. Main OB1 Network Breakdown (LADDER Logic)

### Network 2: Start / Stop & Fail-Safe Safety Interlock
- **Inputs**: `%I10.0` (Start PB), `%I10.1` (Stop PB), `%M8.0` (Python_Alive).
- **Output / Memory**: `%M1.0` (Start_Mem).
- **LADDER Diagram**:
  
  ![Network 2 - Start / Stop & Safety Interlock](../assets/plc_networks/network_2_start_stop.png)

- **Fail-Safe Mechanism**: If Python loses connection, `%M8.0` drops to 0 via Watchdog timeout, immediately breaking the seal and stopping all movement.

---

### Network 3: Part Detection at Vision Inspection Zone
- **Inputs**: `%M1.0` (Start_Mem), `%I10.2` (First_Detected_Sensor), `NOT %M3.0` (Move_Z_Mem).
- **Output**: `DB1.DBX0.1` (`Part_At_Camera`).
- **LADDER Diagram**:
  
  ![Network 3 - Part Detection at Camera Zone](../assets/plc_networks/network_3_part_detection.png)

- **Function**: Signals Python to initiate asynchronous model inference. Disabled if the robot is currently picking up a part.

---

### Network 4: Conveyor Stop Memory (SR Latch)
- **Inputs**: `First_Detected_Sensor` via `Timer1` (`TP 10s`), `DB1.DBX0.0` (Trigger), `%I10.4` (Second_Band_First_Sensor).
- **Output / Memory**: `%M2.0` (Stop_Mem).
- **LADDER Diagram**:
  
  ![Network 4 - Conveyor Stop Memory SR](../assets/plc_networks/network_4_stop_memory_sr.png)

- **Behavior**:
  - `TP 10s` halts the main conveyor for up to 10 seconds while the PCB is under the camera.
  - If a defect trigger arrives (`DB1.DBX0.0`), `Stop_Mem` is latched permanently until the robotic arm clears the board to conveyor 2 (`%I10.4`).

---

### Network 5: Synchronized Main Conveyor Control
- **Logic**: `%M1.0 AND NOT %M2.0`.
- **Physical Actuators**:
  - `%Q10.0`: Main Entry Conveyor Motor.
  - `%Q10.5`: Curved Conveyor Motor.
  - `%Q10.6`: Exit Conveyor Motor.
- **LADDER Diagram**:
  
  ![Network 5 - Main Conveyor Control](../assets/plc_networks/network_5_main_conveyor.png)

---

### Network 6: Defect Processing Memory (SR Latch)
- **SET**: `DB1.DBX0.0` (Python Trigger).
- **RESET**: `%I10.4` (Second_Band_First_Sensor).
- **Memory**: `%M7.0` (`Defect_Process_Active`). Coordinates robotic pick sequence.
- **LADDER Diagram**:
  
  ![Network 6 - Defect Process SR Latch](../assets/plc_networks/network_6_defect_process_sr.png)

---

### Network 7 & 8: Cartesian Pick & Place State Machine
A sequential 3-phase hardware routine:
1. **Z-Descent & Gripper Activation**:
   - `Defect_Process_Active (%M7.0) AND First_Detected_Sensor (%I10.2)` &rarr; SET `%M3.0` (Move_Z_Mem) & SET `%M4.0` (Grab_Mem).
2. **Vacuum Gripped & X-Axis Transfer**:
   - Machine sensor (`%I10.5`) confirms board gripped &rarr; RESET `%M3.0`, SET `%M5.0` (Move_X_Mem).
3. **Release on Reject Line**:
   - Second band sensor (`%I10.4`) triggered &rarr; RESET `%M4.0` (vacuum release), RESET `%M5.0`, RESET `%M3.0` (robot returns home).
   - Driven by physical outputs `%Q10.1` (Z-Axis), `%Q10.2` (Vacuum Gripper), `%Q10.3` (X-Axis).
- **LADDER Diagrams**:
  
  ![Network 7 - Robot Pick & Place Sequence](../assets/plc_networks/network_7_pick_and_place.png)
  
  ![Network 8 - Robot Actuator Output Drivers](../assets/plc_networks/network_8_robot_actuators.png)

---

### Network 9: Second Conveyor Reject Line Control
- **SET**: Activated when defective item is placed on band 2 (`%I10.4`) &rarr; SET `%M6.0` &rarr; Motor `%Q10.4` runs.
- **RESET**: When item passes discharge sensor `%I10.3`, `Timer3` (`TON 1.0s`) delays 1s to allow full clearance before halting motor.
- **LADDER Diagram**:
  
  ![Network 9 - Second Conveyor Control](../assets/plc_networks/network_9_second_conveyor.png)

---

### Network 10: Watchdog Heartbeat & Signal Stack Light
- **Watchdog Timer**: `Timer5` (`TOF - Timer Off-Delay, 1.0s`) fed by `DB1.DBX0.2`.
- If Python stops pulsing for > 1.0 second, `Python_Alive (%M8.0)` drops to `FALSE`.
- **Stack Light Outputs**:
  - **Green (`%Q11.0`)**: `%M1.0 AND %M8.0` (Production Running & AI Connected).
  - **Yellow (`%Q11.1`)**: `NOT %M1.0 AND %M8.0` (Standby / Paused & AI Connected).
  - **Red (`%Q10.7`)**: `NOT %M8.0` (Emergency Stop / Python Offline).
- **LADDER Diagram**:
  
  ![Network 10 - Watchdog & Stack Light](../assets/plc_networks/network_10_watchdog_stacklight.png)

---

## 5. File Inventory & Backup

- `PCB_Sorting_Cell_V18.zap18`: Siemens TIA Portal V18 complete project archive (hardware configuration, OB1 logic, DB1 memory map).
- `assets/plc_networks/`: High-resolution graphical exports of all LADDER networks (Networks 2 through 10).
