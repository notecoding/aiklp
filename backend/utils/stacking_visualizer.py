# backend/utils/stacking_visualizer.py
"""
쌓임 패턴 시각화
"""
import cv2
import numpy as np

def visualize_stacks(image_path, detections, stacks, output_path):
    """
    쌓임 그룹을 이미지에 표시
    
    Args:
        image_path: 원본 이미지
        detections: 전체 탐지 결과
        stacks: detect_stacks() 결과
        output_path: 저장 경로
    """
    img = cv2.imread(image_path)
    
    # 각 쌓임 그룹 표시
    for stack in stacks:
        x1, y1, x2, y2 = map(int, stack['bounding_box'])
        
        # 색상 (high=빨강, medium=주황)
        if stack['severity'] == 'high':
            color = (0, 0, 255)      # 빨강
            label_bg = (0, 0, 200)
        else:
            color = (0, 165, 255)    # 주황
            label_bg = (0, 140, 200)
        
        # 반투명 박스
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
        img = cv2.addWeighted(img, 0.7, overlay, 0.3, 0)
        
        # 테두리
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
        
        # 라벨
        label = f"{stack['type'][:4].upper()}: {stack['object']} x{stack['count']}"
        
        # 라벨 배경
        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(img, (x1, y1 - text_h - 10), (x1 + text_w, y1), label_bg, -1)
        
        # 라벨 텍스트
        cv2.putText(img, label, (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # 통계 표시
    if stacks:
        stats_y = 30
        cv2.putText(img, f"Total Stacks: {len(stacks)}", (10, stats_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
        cv2.putText(img, f"Total Stacks: {len(stacks)}", (10, stats_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        high_count = sum(1 for s in stacks if s['severity'] == 'high')
        if high_count > 0:
            cv2.putText(img, f"High Risk: {high_count}", (10, stats_y + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    cv2.imwrite(output_path, img)
    print(f"✅ 쌓임 시각화 저장: {output_path}")


def draw_stack_connections(image_path, detections, stacks, output_path):
    """
    디버그용: 쌓임 그룹의 물건들을 선으로 연결
    """
    img = cv2.imread(image_path)
    
    for stack in stacks:
        # 그룹 내 모든 물건의 중심점 연결
        centers = []
        for idx in stack['indices']:
            if idx < len(detections):
                bbox = detections[idx]['bbox']
                cx = int((bbox[0] + bbox[2]) / 2)
                cy = int((bbox[1] + bbox[3]) / 2)
                centers.append((cx, cy))
        
        # 선으로 연결
        color = (0, 0, 255) if stack['severity'] == 'high' else (0, 165, 255)
        for i in range(len(centers) - 1):
            cv2.line(img, centers[i], centers[i+1], color, 2)
        
        # 중심점 표시
        for center in centers:
            cv2.circle(img, center, 5, color, -1)
    
    cv2.imwrite(output_path, img)
    print(f"✅ 연결 시각화 저장: {output_path}")
