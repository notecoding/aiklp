import React from "react";

/**
 * AnalysisBox 컴포넌트
 * AI 분석 결과 텍스트와 액션 버튼들을 표시하는 박스
 *
 * @param {Object} props - 컴포넌트 속성
 * @param {string} props.feedback - AI 피드백 텍스트
 * @param {Function} [props.onButton1Click] - 다시 분석하기 버튼 클릭 핸들러
 * @param {Function} [props.onButton2Click] - 결과 저장 버튼 클릭 핸들러
 * @returns {JSX.Element} 결과 텍스트 박스 UI
 */
export function AnalysisBox({ feedback, onButton1Click, onButton2Click }) {
  return (
    <div className="flex w-[1100px] h-[500px] bg-white rounded-2xl shadow-md p-10 flex-col">
      {/* 제목 */}
      <h3 className="text-2xl font-bold text-gray-900 mb-8">
        정리 진단 & 맞춤형 제안
      </h3>

      {/* 분석 결과 텍스트 - whitespace-pre-line으로 줄바꿈 지원 */}
      <div className="flex-1 text-gray-700 text-lg leading-relaxed mb-8 overflow-auto whitespace-pre-line">
        {feedback || "AI가 분석한 결과가 여기에 표시됩니다."}
      </div>

      {/* 하단 버튼들 */}
      <div className="flex gap-4 justify-end">
        <button
          onClick={onButton1Click}
          className="px-10 py-3.5 bg-blue-500 text-white text-base font-semibold rounded-full hover:bg-blue-600 transition-colors shadow-md"
        >
          다시 분석하기
        </button>
        <button
          onClick={onButton2Click}
          className="px-10 py-3.5 bg-green-500 text-white text-base font-semibold rounded-full hover:bg-green-600 transition-colors shadow-md"
        >
          결과 저장
        </button>
      </div>
    </div>
  );
}