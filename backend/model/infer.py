from ultralytics import YOLO
import cv2
import os

# YOLO 모델 로드 (사전 학습된 .pt 파일 필요)
model = YOLO("yolov8x.pt")

def run_inference(image_path, result_dir):
    """
    입력 이미지를 YOLO 모델로 분석하고,
    탐지 결과와 시각화 이미지를 반환합니다.
    """
    results = model.predict(source=image_path, conf=0.4)

    detections = []
    img = cv2.imread(image_path)

    for box in results[0].boxes:
        cls = int(box.cls[0])
        name = model.names[cls]
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        detections.append({
            "name": name,
            "conf": round(conf, 2),
            "bbox": [x1, y1, x2, y2]
        })

        # 감지된 객체 표시
        color = (0, 0, 255) if "바닥" in name or "쌓임" in name else (0, 255, 0)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, f"{name} ({conf:.2f})", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 결과 이미지 저장
    result_path = os.path.join(result_dir, os.path.basename(image_path))
    cv2.imwrite(result_path, img)

    return detections, result_path
