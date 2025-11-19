# backend/db.py
# 분석 기록 데이터베이스 관리

import sqlite3
from datetime import datetime
import json

DB_PATH = 'analysis_history.db'

def init_db():
    """데이터베이스 초기화"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_objects INTEGER NOT NULL,
            floor_items INTEGER NOT NULL,
            image_name TEXT NOT NULL,
            detections TEXT,
            suggestions TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 데이터베이스 초기화 완료")

def save_analysis(score, detections, report, image_name):
    """분석 결과 저장"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 바닥 물건 개수
    max_y = max(obj['bbox'][3] for obj in detections) if detections else 1000
    floor_items = sum(1 for d in detections if d['bbox'][3] > max_y * 0.8)
    
    c.execute('''
        INSERT INTO analyses (
            timestamp, score, total_objects, floor_items, 
            image_name, detections, suggestions
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        score,
        len(detections),
        floor_items,
        image_name,
        json.dumps(detections),
        json.dumps(report.get('suggestions', []))
    ))
    
    conn.commit()
    analysis_id = c.lastrowid
    conn.close()
    
    return analysis_id

def get_history(limit=10):
    """전체 기록 조회"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT id, timestamp, score, total_objects, floor_items, image_name
        FROM analyses
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    return [{
        'id': r[0],
        'timestamp': r[1],
        'score': r[2],
        'total_objects': r[3],
        'floor_items': r[4],
        'image_name': r[5]
    } for r in rows]

def get_statistics():
    """통계 조회"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 전체 분석 횟수
    c.execute('SELECT COUNT(*) FROM analyses')
    total_count = c.fetchone()[0]
    
    # 평균 점수
    c.execute('SELECT AVG(score) FROM analyses')
    avg_score = c.fetchone()[0] or 0
    
    # 최고 점수
    c.execute('SELECT MAX(score) FROM analyses')
    max_score = c.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_analyses': total_count,
        'average_score': round(avg_score, 1),
        'max_score': max_score
    }