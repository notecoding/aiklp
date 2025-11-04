import math

def analyze_results(detections):
    """
    YOLO 탐지 결과를 기반으로 방 정리 행동 가이드를 생성합니다.
    - 각 객체의 bbox 좌표를 이용해 위치 관계를 분석
    - 사물 간 거리 기반으로 "책상 위 책", "바닥 근처 옷" 같은 문장 생성
    """

    total = len(detections)
    if total == 0:
        return {"score": 100, "issues": [], "suggestions": ["정리 상태가 매우 양호합니다!"]}

    objects = [d["name"].lower() for d in detections]
    positions = {d["name"].lower(): d["bbox"] for d in detections}
    suggestions = []
    issues = []
    score = 100

    # --------------------
    # 유틸리티 함수
    # --------------------
    def center(bbox):
        x1, y1, x2, y2 = bbox
        return (x1 + x2) / 2, (y1 + y2) / 2

    def is_above(bbox1, bbox2, threshold=40):
        """bbox1이 bbox2 위에 있는지"""
        _, y1 = center(bbox1)
        _, y2 = center(bbox2)
        return (y1 + threshold) < y2

    def distance(bbox1, bbox2):
        """두 객체 중심 간 거리"""
        x1, y1 = center(bbox1)
        x2, y2 = center(bbox2)
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    # --------------------
    # 분석 로직 시작
    # --------------------
    for d in detections:
        name = d["name"].lower()
        bbox = d["bbox"]

        # 책 관련 분석
        if "book" in name:
            issues.append("book")

            # 책상 위에 있을 경우
            if "desk" in positions and is_above(bbox, positions["desk"]):
                if "drawer" in positions:
                    suggestions.append("책상 위의 책을 서랍에 정리하세요.")
                else:
                    suggestions.append("책상 위의 책을 정리하세요.")
                score -= 10
            elif "drawer" in positions:
                suggestions.append("책을 서랍에 보관하세요.")
                score -= 5
            elif "shelf" in positions or "cabinet" in positions:
                suggestions.append("책을 책장에 꽂아 정리하세요.")
                score -= 5
            else:
                suggestions.append("책을 정리된 곳에 보관하세요.")
                score -= 5

        # 옷 관련 분석
        elif "clothes" in name or "shirt" in name:
            issues.append("clothes")
            y_bottom = bbox[3]

            # 바닥 근처 판단 (이미지 아래쪽 20%)
            if y_bottom > 0.8 * max(b[3] for b in positions.values()):
                if "closet" in positions:
                    suggestions.append("바닥에 있는 옷을 옷장에 정리하세요.")
                elif "drawer" in positions:
                    suggestions.append("바닥의 옷을 서랍에 넣으세요.")
                else:
                    suggestions.append("바닥의 옷을 치워주세요.")
                score -= 15

        # 컵 / 병 관련
        elif "cup" in name or "bottle" in name:
            issues.append("cup/bottle")
            if "sink" in positions:
                suggestions.append("컵이나 병을 싱크대로 옮기세요.")
            elif "cabinet" in positions:
                suggestions.append("컵이나 병을 수납장에 정리하세요.")
            else:
                suggestions.append("컵이나 병을 치워주세요.")
            score -= 5

        # 의자 관련
        elif "chair" in name:
            issues.append("chair")
            suggestions.append("의자 주변을 정리해보세요.")
            score -= 3

    # --------------------
    # 중복 제거 및 점수 보정
    # --------------------
    suggestions = list(set(suggestions))
    score = max(0, score)

    return {
        "score": score,
        "issues": issues,
        "suggestions": suggestions
    }
