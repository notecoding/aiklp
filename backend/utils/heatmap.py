# backend/utils/heatmap.py
# 정리 필요 구역 히트맵 시각화

import cv2
import numpy as np

def generate_heatmap(image_path, detections, output_path):
    """
    정리 필요 구역 히트맵 생성
    
    Args:
        image_path: 원본 이미지 경로
        detections: YOLO 탐지 결과 리스트
        output_path: 히트맵 저장 경로
    
    Returns:
        str: 저장된 히트맵 경로
    """
    
    # 원본 이미지 읽기
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")
    
    height, width = img.shape[:2]
    
    # 빈 히트맵 생성
    heatmap = np.zeros((height, width), dtype=np.float32)
    
    # 바닥 기준선
    floor_threshold = height * 0.8
    
    # 각 객체마다 열(heat) 추가
    for obj in detections:
        x1, y1, x2, y2 = obj['bbox']
        
        # 좌표 보정
        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(width, int(x2))
        y2 = min(height, int(y2))
        
        # 중심점
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        
        # 반경 (객체 크기)
        radius = max((x2 - x1), (y2 - y1)) // 2
        radius = max(radius, 20)  # 최소 반경
        
        # 바닥 물건은 더 뜨겁게
        heat_value = 3.0 if y2 > floor_threshold else 1.0
        
        # 물건 종류별 가중치
        name = obj['name'].lower()
        if any(x in name for x in ['book', 'backpack', 'suitcase']):
            heat_value *= 1.5
        elif any(x in name for x in ['cup', 'bottle']):
            heat_value *= 1.3
        
        # 가우시안 분포로 열 추가
        y_coords, x_coords = np.ogrid[:height, :width]
        mask = ((x_coords - cx) ** 2 + (y_coords - cy) ** 2) <= (radius ** 2)
        distances = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2)
        gaussian = np.exp(-(distances ** 2) / (2 * (radius / 2) ** 2))
        
        heatmap += gaussian * heat_value * mask
    
    # 히트맵이 비어있으면 원본 반환
    if heatmap.max() == 0:
        cv2.imwrite(output_path, img)
        return output_path
    
    # 정규화 (0-255)
    heatmap_normalized = np.uint8(255 * heatmap / heatmap.max())
    
    # JET 컬러맵 적용 (파랑→초록→빨강)
    heatmap_color = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)
    
    # 원본과 합성 (60% 원본 + 40% 히트맵)
    result = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)
    
    # 저장
    cv2.imwrite(output_path, result)
    
    return output_path