# backend/utils/room_segmentation.py
"""
YOLOv8 Segmentation 기반 방 구역 분석
- 바닥, 침대, 책상, 가구 등을 픽셀 단위로 정확히 구분
"""
from ultralytics import YOLO
import cv2
import numpy as np

# Segmentation 모델 싱글톤
_seg_model = None

def get_segmentation_model():
    """YOLOv8-seg 모델 로드 (싱글톤)"""
    global _seg_model
    if _seg_model is None:
        print("📥 YOLOv8-seg 모델 로드 중...")
        _seg_model = YOLO("yolov8x-seg.pt")
        print("✅ 모델 로드 완료")
    return _seg_model


def segment_room_areas(image_path):
    """
    방 이미지를 구역별로 분할
    
    Returns:
        dict: {
            'floor_mask': np.array,
            'bed_mask': np.array,
            'desk_mask': np.array,
            'furniture_mask': np.array,
            'detected_areas': list
        }
    """
    model = get_segmentation_model()
    
    # Segmentation 수행
    results = model.predict(source=image_path, conf=0.3, verbose=False)
    
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    
    # 빈 마스크 생성
    floor_mask = np.zeros((h, w), dtype=np.uint8)
    bed_mask = np.zeros((h, w), dtype=np.uint8)
    desk_mask = np.zeros((h, w), dtype=np.uint8)
    furniture_mask = np.zeros((h, w), dtype=np.uint8)
    
    detected_areas = []
    
    # 각 감지된 객체에 대해 마스크 생성
    for result in results:
        if result.masks is None:
            continue
            
        for i, (mask, box) in enumerate(zip(result.masks.data, result.boxes)):
            cls = int(box.cls[0])
            name = model.names[cls].lower()
            conf = float(box.conf[0])
            
            # 마스크를 원본 이미지 크기로 리사이즈
            mask_resized = cv2.resize(
                mask.cpu().numpy(),
                (w, h),
                interpolation=cv2.INTER_LINEAR
            )
            mask_binary = (mask_resized > 0.5).astype(np.uint8)
            
            # 구역별로 마스크 누적
            if 'bed' in name:
                bed_mask = cv2.bitwise_or(bed_mask, mask_binary)
                detected_areas.append({'type': 'bed', 'confidence': conf})
                
            elif any(x in name for x in ['desk', 'table', 'dining table']):
                desk_mask = cv2.bitwise_or(desk_mask, mask_binary)
                detected_areas.append({'type': 'desk', 'confidence': conf})
                
            elif any(x in name for x in ['chair', 'couch', 'sofa']):
                furniture_mask = cv2.bitwise_or(furniture_mask, mask_binary)
                detected_areas.append({'type': 'furniture', 'confidence': conf})
    
    # 바닥 마스크: 하단 30% 영역 중 다른 마스크가 없는 곳
    floor_region = np.zeros((h, w), dtype=np.uint8)
    floor_region[int(h * 0.7):, :] = 1
    
    occupied = cv2.bitwise_or(bed_mask, desk_mask)
    occupied = cv2.bitwise_or(occupied, furniture_mask)
    
    floor_mask = cv2.bitwise_and(floor_region, cv2.bitwise_not(occupied))
    
    return {
        'floor_mask': floor_mask,
        'bed_mask': bed_mask,
        'desk_mask': desk_mask,
        'furniture_mask': furniture_mask,
        'detected_areas': detected_areas
    }


def detect_object_location_precise(bbox, room_masks):
    """
    bbox 중심점이 어느 구역에 속하는지 판단
    
    Args:
        bbox: [x1, y1, x2, y2]
        room_masks: segment_room_areas()의 리턴값
    
    Returns:
        str: 'floor', 'bed_surface', 'desk', 'furniture', 'normal'
    """
    x1, y1, x2, y2 = bbox
    cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
    
    # 각 마스크에서 중심점 체크
    if room_masks['bed_mask'][cy, cx] > 0:
        return 'bed_surface'
    elif room_masks['desk_mask'][cy, cx] > 0:
        return 'desk'
    elif room_masks['furniture_mask'][cy, cx] > 0:
        return 'furniture'
    elif room_masks['floor_mask'][cy, cx] > 0:
        return 'floor'
    else:
        return 'normal'


def calculate_area_coverage(room_masks):
    """
    각 구역이 차지하는 비율 계산
    
    Returns:
        dict: {'floor': 0.25, 'bed': 0.15, ...}
    """
    total_pixels = room_masks['floor_mask'].size
    
    return {
        'floor': np.sum(room_masks['floor_mask'] > 0) / total_pixels,
        'bed': np.sum(room_masks['bed_mask'] > 0) / total_pixels,
        'desk': np.sum(room_masks['desk_mask'] > 0) / total_pixels,
        'furniture': np.sum(room_masks['furniture_mask'] > 0) / total_pixels
    }


def visualize_room_zones(image_path, room_masks, output_path):
    """
    구역을 색상으로 시각화
    
    Args:
        image_path: 원본 이미지
        room_masks: segment_room_areas()의 리턴값
        output_path: 저장 경로
    """
    img = cv2.imread(image_path)
    
    # 색상 정의
    colors = {
        'floor': (0, 0, 255),      # 빨강
        'bed': (0, 255, 255),      # 노랑
        'desk': (0, 255, 0),       # 초록
        'furniture': (255, 128, 0) # 주황
    }
    
    overlay = img.copy()
    
    # 각 마스크를 반투명 색상으로 표시
    for area_name, color in colors.items():
        mask = room_masks[f'{area_name}_mask']
        overlay[mask > 0] = color
    
    # 원본과 합성
    result = cv2.addWeighted(img, 0.6, overlay, 0.4, 0)
    
    # 범례 추가
    legend_y = 30
    for area_name, color in colors.items():
        cv2.rectangle(result, (10, legend_y), (40, legend_y + 20), color, -1)
        cv2.putText(result, area_name.capitalize(), (50, legend_y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        legend_y += 30
    
    cv2.imwrite(output_path, result)
    print(f"✅ 구역 시각화 저장: {output_path}")
