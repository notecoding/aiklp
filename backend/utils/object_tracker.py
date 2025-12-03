# backend/utils/object_tracker.py
"""
객체 추적 시스템 (IoU 기반)
- 여러 번 업로드된 이미지에서 같은 물건 추적
- 반복적으로 문제를 일으키는 물건 식별
"""
import json
import os
from datetime import datetime, timedelta
import numpy as np

class SimpleObjectTracker:
    """간단한 IoU 기반 객체 추적기"""
    
    def __init__(self, iou_threshold=0.3, state_file='tracker_state.json'):
        self.iou_threshold = iou_threshold
        self.state_file = state_file
        self.tracks = {}  # {track_id: {...}}
        self.next_track_id = 0
        
        # 상태 로드
        self._load_state()
    
    def _load_state(self):
        """저장된 추적 상태 로드"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tracks = data.get('tracks', {})
                    self.next_track_id = data.get('next_track_id', 0)
                print(f"✅ 추적 상태 로드: {len(self.tracks)}개 트랙")
            except Exception as e:
                print(f"⚠️ 상태 로드 실패: {e}")
    
    def _save_state(self):
        """추적 상태 저장"""
        try:
            data = {
                'tracks': self.tracks,
                'next_track_id': self.next_track_id
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 상태 저장 실패: {e}")
    
    def iou(self, bbox1, bbox2):
        """IoU 계산"""
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
    
    def update(self, detections, image_name):
        """
        새로운 프레임의 탐지 결과로 추적 업데이트
        
        Args:
            detections: YOLO 탐지 결과 리스트
            image_name: 이미지 파일명
        """
        timestamp = datetime.now().isoformat()
        
        # 기존 트랙과 매칭
        matched_tracks = set()
        
        for detection in detections:
            bbox = detection['bbox']
            obj_name = detection['name']
            location = detection.get('location', 'unknown')
            
            # 가장 유사한 트랙 찾기
            best_track_id = None
            best_iou = 0
            
            for track_id, track in self.tracks.items():
                # 같은 물체 종류만 비교
                if track['object'] != obj_name:
                    continue
                
                # 최근 bbox와 IoU 계산
                last_bbox = track['history'][-1]['bbox']
                current_iou = self.iou(bbox, last_bbox)
                
                if current_iou > self.iou_threshold and current_iou > best_iou:
                    best_iou = current_iou
                    best_track_id = track_id
            
            # 매칭된 트랙 업데이트
            if best_track_id is not None:
                self.tracks[best_track_id]['history'].append({
                    'bbox': bbox,
                    'location': location,
                    'timestamp': timestamp,
                    'image': image_name
                })
                self.tracks[best_track_id]['last_seen'] = timestamp
                matched_tracks.add(best_track_id)
            
            # 새 트랙 생성
            else:
                new_track_id = str(self.next_track_id)
                self.next_track_id += 1
                
                self.tracks[new_track_id] = {
                    'object': obj_name,
                    'first_seen': timestamp,
                    'last_seen': timestamp,
                    'history': [{
                        'bbox': bbox,
                        'location': location,
                        'timestamp': timestamp,
                        'image': image_name
                    }]
                }
                matched_tracks.add(new_track_id)
        
        # 오래된 트랙 정리 (7일 이상 안 보인 것)
        self._cleanup_old_tracks(days=7)
        
        # 상태 저장
        self._save_state()
    
    def _cleanup_old_tracks(self, days=7):
        """오래된 트랙 제거"""
        cutoff = datetime.now() - timedelta(days=days)
        
        to_remove = []
        for track_id, track in self.tracks.items():
            last_seen = datetime.fromisoformat(track['last_seen'])
            if last_seen < cutoff:
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.tracks[track_id]
    
    def get_problem_objects(self, min_appearances=3):
        """
        반복적으로 문제를 일으키는 물건 찾기
        
        Args:
            min_appearances: 최소 출현 횟수
        
        Returns:
            list: 문제 물건 리스트
        """
        problems = []
        
        for track_id, track in self.tracks.items():
            total_appearances = len(track['history'])
            
            if total_appearances < min_appearances:
                continue
            
            # 문제 위치 카운트
            problem_locations = ['floor', 'bed_surface']
            problem_count = sum(
                1 for h in track['history']
                if h['location'] in problem_locations
            )
            
            # 문제 비율
            problem_ratio = problem_count / total_appearances
            
            if problem_count >= min_appearances:
                problems.append({
                    'track_id': track_id,
                    'object': track['object'],
                    'total_appearances': total_appearances,
                    'problem_count': problem_count,
                    'problem_ratio': problem_ratio,
                    'first_seen': track['first_seen'],
                    'last_seen': track['last_seen'],
                    'message': f"{track['object']}이(가) {problem_count}번 문제 위치에서 발견되었습니다"
                })
        
        # 문제 심각도 순 정렬
        problems.sort(key=lambda x: (x['problem_count'], x['problem_ratio']), reverse=True)
        
        return problems
    
    def get_statistics(self):
        """추적 통계"""
        if not self.tracks:
            return {
                'total_tracks': 0,
                'active_tracks': 0,
                'most_common_object': None
            }
        
        # 물체별 카운트
        object_counts = {}
        for track in self.tracks.values():
            obj = track['object']
            object_counts[obj] = object_counts.get(obj, 0) + 1
        
        most_common = max(object_counts.items(), key=lambda x: x[1]) if object_counts else (None, 0)
        
        return {
            'total_tracks': len(self.tracks),
            'active_tracks': len(self.tracks),
            'most_common_object': most_common[0],
            'object_counts': object_counts
        }
    
    def reset(self):
        """모든 추적 정보 초기화"""
        self.tracks = {}
        self.next_track_id = 0
        self._save_state()
        print("✅ 추적 정보 초기화됨")

# 싱글톤 인스턴스
_tracker = None

def get_tracker():
    """SimpleObjectTracker 싱글톤"""
    global _tracker
    if _tracker is None:
        _tracker = SimpleObjectTracker()
    return _tracker
