import React from "react";

/**
 * ScoreBox 컴포넌트
 * 분석 대상 이미지와 점수를 표시하는 섹션
 * 점수에 따라 동적으로 상태 메시지와 색상이 변경됨
 *
 * @param {Object} props - 컴포넌트 속성
 * @param {string} props.imageSrc - 표시할 이미지 URL
 * @param {number} props.score - 현재 점수 (0-100)
 * @param {number} [props.maxScore=100] - 최대 점수
 * @returns {JSX.Element} 이미지 섹션 UI
 */
export function ScoreBox({ imageSrc, score = 0, maxScore = 100 }) {
  /**
   * 점수에 따라 상태 메시지와 색상 결정
   * @returns {{ message: string, color: string, bgColor: string }}
   */
  const getScoreStatus = () => {
    if (score >= 90) {
      return {
        message: "완벽해요!",
        color: "text-green-600",
        bgColor: "bg-green-50",
      };
    } else if (score >= 80) {
      return {
        message: "매우 깔끔",
        color: "text-blue-600",
        bgColor: "bg-blue-50",
      };
    } else if (score >= 70) {
      return {
        message: "깔끔함",
        color: "text-teal-600",
        bgColor: "bg-teal-50",
      };
    } else if (score >= 60) {
      return {
        message: "보통",
        color: "text-yellow-600",
        bgColor: "bg-yellow-50",
      };
    } else if (score >= 40) {
      return {
        message: "정리 필요",
        color: "text-orange-600",
        bgColor: "bg-orange-50",
      };
    } else {
      return {
        message: "많이 어질러짐",
        color: "text-red-600",
        bgColor: "bg-red-50",
      };
    }
  };

  const status = getScoreStatus();

  return (
    <div className="flex flex-col gap-6 h-full">
      {/* 이미지 영역 */}
      <div className="flex w-[550px] h-[400px] bg-gray-200 rounded-2xl flex items-center justify-center overflow-hidden shadow-md">
        {imageSrc ? (
          <img
            src={imageSrc}
            alt="분석 이미지"
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-gray-400 text-lg font-medium">이미지</span>
        )}
      </div>

      {/* 점수 박스 */}
      <div className={`${status.bgColor} rounded-2xl px-8 py-6 shadow-md flex-shrink-0 border-2 border-gray-200`}>
        <div className="text-center">
          <p className="text-gray-700 text-base mb-2">최종 점수</p>
          <div className="flex items-center justify-center gap-3">
            <span className={`font-bold text-4xl ${status.color}`}>
              {score}점
            </span>
            <span className="text-gray-400 text-lg">/ {maxScore}점</span>
          </div>
          <p className={`${status.color} text-lg font-semibold mt-3`}>
            ({status.message})
          </p>
        </div>
      </div>
    </div>
  );
}