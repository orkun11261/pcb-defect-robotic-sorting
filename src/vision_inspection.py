import time
import threading
import cv2
import snap7
from snap7.util import get_bool, set_bool
from ultralytics import YOLO

PLC_IP = 'your_ip'
RACK = 0
SLOT = 1
DB_NUM = 1
TIMEOUT_LIMIT = 10.0

model = YOLO("your_model")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Camera open failed.")

client = snap7.client.Client()
client.connect(PLC_IP, RACK, SLOT)
if not client.get_connected():
    raise SystemExit("PLC connection failed.")

lock = threading.Lock()
busy = False
defect_flag = False
defect_boxes = 0
annotated_frame = None

def worker_predict(img):
    global busy, defect_flag, defect_boxes, annotated_frame
    res = model(img, conf=0.5, verbose=False)
    boxes = res[0].boxes
    with lock:
        defect_boxes = len(boxes)
        if defect_boxes > 0:
            defect_flag = True
            annotated_frame = res[0].plot()
        else:
            annotated_frame = None
        busy = False

active_session = False
session_start = 0.0
trigger_sent = False
prev_sensor = False
status_msg = "IDLE"
status_color = (200, 200, 200)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        db_buffer = client.db_read(DB_NUM, 0, 1)
        sensor_active = get_bool(db_buffer, 0, 1)
        now = time.time()

        if sensor_active and not prev_sensor:
            active_session = True
            session_start = now
            trigger_sent = False
            with lock:
                defect_flag = False
                defect_boxes = 0
                annotated_frame = None

        if active_session and not trigger_sent:
            remaining = TIMEOUT_LIMIT - (now - session_start)

            if remaining > 0:
                with lock:
                    is_busy = busy
                    has_defect = defect_flag
                    cnt = defect_boxes

                if not is_busy and not has_defect:
                    busy = True
                    threading.Thread(target=worker_predict, args=(frame.copy(),), daemon=True).start()

                if has_defect:
                    status_msg = f"DEFECT DETECTED ({cnt})"
                    status_color = (0, 0, 255)
                    set_bool(db_buffer, 0, 0, True)
                    client.db_write(DB_NUM, 0, db_buffer)
                    trigger_sent = True
                    active_session = False
                else:
                    status_msg = f"SCANNING ({remaining:.1f}s)"
                    status_color = (0, 255, 255)
            else:
                status_msg = "PASS (CLEAN)"
                status_color = (0, 255, 0)
                set_bool(db_buffer, 0, 0, False)
                client.db_write(DB_NUM, 0, db_buffer)
                trigger_sent = True
                active_session = False

        if not sensor_active and prev_sensor:
            set_bool(db_buffer, 0, 0, False)
            client.db_write(DB_NUM, 0, db_buffer)
            active_session = False
            trigger_sent = False
            with lock:
                defect_flag = False
                defect_boxes = 0
                annotated_frame = None
            status_msg = "IDLE"
            status_color = (200, 200, 200)

        prev_sensor = sensor_active

        out_frame = frame
        with lock:
            if annotated_frame is not None:
                out_frame = annotated_frame

        cv2.putText(out_frame, f"STATUS: {status_msg}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2)

        sens_indicator = (0, 255, 0) if sensor_active else (0, 0, 255)
        h, w, _ = out_frame.shape
        cv2.circle(out_frame, (w - 30, 30), 8, sens_indicator, -1)

        set_bool(db_buffer, 0, 2, True)
        client.db_write(DB_NUM, 0, db_buffer)

        cv2.imshow("Vision Inspection", out_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

finally:
    try:
        if client.get_connected():
            buf = client.db_read(DB_NUM, 0, 1)
            set_bool(buf, 0, 0, False)
            set_bool(buf, 0, 2, False)
            client.db_write(DB_NUM, 0, buf)
    except Exception:
        pass
    cap.release()
    cv2.destroyAllWindows()
    client.disconnect()