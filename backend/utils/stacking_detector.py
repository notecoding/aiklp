# backend/utils/stacking_detector.py
"""
물체 쌓임/포개짐 자동 감지
- 수직 쌓임: 책, 박스 등이 수직으로 쌓인 경우
- 포개짐: 옷, 서류 등이 포개진 경우
"""
import numpy as np
from collections import defaultdict

class StackingDetector:
    """물체 쌓임 감지 클래스"""
    
    def __init__(self, iou_threshold=0.3, vertical_gap_max=50, min_stack_count=3):
        self.iou_threshold = iou_threshold
        self.vertical_gap_max = vertical_gap_max
        self.min_stack_count = min_stack_count
    
    def calculate_iou(self, bbox1, bbox2):
        """IoU (Intersection over Union) 계산"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        xi1 = max(x1_1, x1_2)
        yi1 = max(y1_1, y1_2)
        xi2 = min(x2_1, x2_2)
        yi2 = min(y2_1, y2_2)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        
        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0
    
    def calculate_overlap_ratio(self, bbox1, bbox2):
        """더 엄격한 중첩 비율"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        xi1 = max(x1_1, x1_2)
        yi1 = max(y1_1, y1_2)
        xi2 = min(x2_1, x2_2)
        yi2 = min(y2_1, y2_2)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        min_area = min((x2_1 - x1_1) * (y2_1 - y1_1), (x2_2 - x1_2) * (y2_2 - y1_2))
        
        return inter_area / min_area if min_area > 0 else 0
    
    def is_vertical_stack(self, bbox1, bbox2):
        """두 물체가 수직으로 쌓여있는지 판단"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # 중심점
        cx1 = (x1_1 + x2_1) / 2
        cx2 = (x1_2 + x2_2) / 2
        
        # 너비
        w1 = x2_1 - x1_1
        w2 = x2_2 - x1_2
        
        # 조건 1: 수평 중심이 비슷함 (너비의 30% 이내)
        horizontal_aligned = abs(cx1 - cx2) < max(w1, w2) * 0.3
        
        # 조건 2: 수직 간격이 작음
        if y2_1 < y1_2:
            vertical_gap = y1_2 - y2_1
        elif y2_2 < y1_1:
            vertical_gap = y1_1 - y2_2
        else:
            vertical_gap = 0
        
        vertical_close = vertical_gap < self.vertical_gap_max
        
        # 조건 3: 크기가 비슷함
        size_similar = abs(w1 - w2) < max(w1, w2) * 0.5
        
        return horizontal_aligned and vertical_close and size_similar
    
    def detect_stacks(self, detections):
        """
        쌓임 패턴 탐지
        
        Returns:
            list: [{'type': 'vertical_stack', 'object': 'book', 'count': 5, ...}, ...]
        """
        if not detections:
            return []
        
        # 물체 종류별로 그룹화
        grouped = defaultdict(list)
        for i, det in enumerate(detections):
            grouped[det['name']].append((i, det))
        
        stacks = []
        
        for obj_name, items in grouped.items():
            if len(items) < self.min_stack_count:
                continue
            
            # 수직 쌓임 탐지
            vertical_stacks = self._find_vertical_stacks(items)
            stacks.extend(vertical_stacks)
            
            # 포개짐 탐지
            overlapping_piles = self._find_overlapping_piles(items)
            stacks.extend(overlapping_piles)
        
        return stacks
    
    def _find_vertical_stacks(self, items):
        """수직으로 쌓인 물건 찾기"""
        stacks = []
        visited = set()
        
        for i, (idx1, det1) in enumerate(items):
            if idx1 in visited:
                continue
            
            stack_group = [idx1]
            
            for j, (idx2, det2) in enumerate(items[i+1:], start=i+1):
                if idx2 in visited:
                    continue
                
                # 스택의 어떤 물건이든 하나와 수직 관계면 추가
                for stack_idx in stack_group:
                    stack_det = items[[x[0] for x in items].index(stack_idx)][1]
                    if self.is_vertical_stack(stack_det['bbox'], det2['bbox']):
                        stack_group.append(idx2)
                        break
            
            if len(stack_group) >= self.min_stack_count:
                visited.update(stack_group)
                
                # Bounding box 계산
                all_bboxes = [items[[x[0] for x in items].index(idx)][1]['bbox'] for idx in stack_group]
                x1 = min(b[0] for b in all_bboxes)
                y1 = min(b[1] for b in all_bboxes)
                x2 = max(b[2] for b in all_bboxes)
                y2 = max(b[3] for b in all_bboxes)
                
                stacks.append({
                    'type': 'vertical_stack',
                    'object': items[0][1]['name'],
                    'count': len(stack_group),
                    'indices': stack_group,
                    'bounding_box': [x1, y1, x2, y2],
                    'severity': 'high' if len(stack_group) >= 5 else 'medium',
                    'message': f"{items[0][1]['name']} {len(stack_group)}개가 수직으로 쌓여있습니다"
                })
        
        return stacks
    
    def _find_overlapping_piles(self, items):
        """포개진 물건 찾기"""
        piles = []
        
        # 중첩 그래프 생성
        n = len(items)
        overlap_graph = [[] for _ in range(n)]
        
        for i in range(n):
            for j in range(i+1, n):
                bbox1 = items[i][1]['bbox']
                bbox2 = items[j][1]['bbox']
                
                overlap = self.calculate_overlap_ratio(bbox1, bbox2)
                if overlap > 0.2:  # 20% 이상 중첩
                    overlap_graph[i].append(j)
                    overlap_graph[j].append(i)
        
        # 연결된 컴포넌트 찾기 (DFS)
        visited = set()
        
        for i in range(n):
            if i in visited:
                continue
            
            # DFS로 연결된 모든 노드 찾기
            stack = [i]
            component = []
            
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                component.append(node)
                
                for neighbor in overlap_graph[node]:
                    if neighbor not in visited:
                        stack.append(neighbor)
            
            if len(component) >= self.min_stack_count:
                all_bboxes = [items[idx][1]['bbox'] for idx in component]
                x1 = min(b[0] for b in all_bboxes)
                y1 = min(b[1] for b in all_bboxes)
                x2 = max(b[2] for b in all_bboxes)
                y2 = max(b[3] for b in all_bboxes)
                
                piles.append({
                    'type': 'overlapping_pile',
                    'object': items[0][1]['name'],
                    'count': len(component),
                    'indices': [items[idx][0] for idx in component],
                    'bounding_box': [x1, y1, x2, y2],
                    'severity': 'high' if len(component) >= 5 else 'medium',
                    'message': f"{items[0][1]['name']} {len(component)}개가 포개져있습니다"
                })
        
        return piles
    
    def calculate_stacking_score(self, stacks):
        """쌓임에 대한 감점 계산"""
        penalty = 0
        
        for stack in stacks:
            if stack['type'] == 'vertical_stack':
                # 수직 쌓임: 더 위험함
                if stack['count'] >= 5:
                    penalty += 15
                elif stack['count'] >= 3:
                    penalty += 10
            
            elif stack['type'] == 'overlapping_pile':
                # 포개짐: 덜 위험하지만 정리 필요
                if stack['count'] >= 5:
                    penalty += 10
                elif stack['count'] >= 3:
                    penalty += 6
        
        return penalty

# 싱글톤 인스턴스
_detector = None

def get_stacking_detector():
    """StackingDetector 싱글톤"""
    global _detector
    if _detector is None:
        _detector = StackingDetector()
    return _detector
