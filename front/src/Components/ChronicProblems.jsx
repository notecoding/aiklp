// src/Components/ChronicProblems.jsx
import React from "react";
import { AlertTriangle, TrendingUp } from "lucide-react";

/**
 * 반복 문제 컴포넌트
 * - 같은 물건이 계속 문제 위치에 나타나는 경우 표시
 */
export function ChronicProblems({ problems, statistics }) {
  if (!problems || problems.length === 0) return null;

  return (
    <div className="bg-red-50 border-2 border-red-300 rounded-xl p-5 mb-4">
      {/* 헤더 */}
      <div className="flex items-center gap-3 mb-3">
        <AlertTriangle size={24} className="text-red-600" />
        <h4 className="text-lg font-bold text-red-800">
          🔄 반복되는 문제: {problems.length}개
        </h4>
      </div>

      {/* 문제 목록 */}
      <div className="space-y-2">
        {problems.map((problem, idx) => (
          <div
            key={idx}
            className="bg-white rounded-lg p-3 border border-red-200"
          >
            <div className="flex justify-between items-center">
              <div className="flex-1">
                <span className="font-bold text-lg">{problem.object}</span>
                <p className="text-sm text-red-700 mt-1">{problem.message}</p>
                <div className="text-xs text-gray-600 mt-1">
                  첫 발견: {new Date(problem.first_seen).toLocaleDateString()}
                </div>
              </div>
              <div className="text-right ml-4">
                <div className="text-2xl font-bold text-red-800">
                  {problem.problem_count}회
                </div>
                <div className="text-xs text-gray-600">
                  ({Math.round(problem.problem_ratio * 100)}%)
                </div>
              </div>
            </div>

            {/* 진행률 바 */}
            <div className="mt-3">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-600 h-2 rounded-full"
                  style={{ width: `${problem.problem_ratio * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 통계 */}
      {statistics && (
        <div className="mt-4 pt-4 border-t border-red-200">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-white rounded-lg p-2 border border-red-100">
              <div className="text-gray-600">총 추적 물건</div>
              <div className="text-xl font-bold text-red-800">
                {statistics.total_tracks}개
              </div>
            </div>
            {statistics.most_common_object && (
              <div className="bg-white rounded-lg p-2 border border-red-100">
                <div className="text-gray-600">가장 흔한 물건</div>
                <div className="text-lg font-bold text-red-800">
                  {statistics.most_common_object}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 조언 */}
      <div className="mt-3 p-3 bg-red-100 rounded-lg">
        <TrendingUp size={16} className="inline text-red-700 mr-2" />
        <span className="text-sm text-red-800 font-medium">
          💡 팁: 반복적으로 문제가 되는 물건은 전용 수납공간을 만들어주세요!
        </span>
      </div>
    </div>
  );
}
