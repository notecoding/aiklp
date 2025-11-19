import React from "react";

export function AnalysisBox({
  feedback,
  aiAdvice = "",
  onButton1Click,
  onButton2Click
}) {
  return (
    <div className="flex w-[1100px] h-[500px] bg-white rounded-2xl shadow-md p-10 flex-col">

      {/* 제목 */}
      <h3 className="text-2xl font-bold text-gray-900 mb-4">
        정리 진단 & 맞춤형 제안
      </h3>

      {/* 🔥 ChatGPT 정리 코칭을 가장 위로 올림 */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-300 rounded-xl p-5 shadow-inner mb-6">
        <h4 className="text-xl font-bold text-yellow-800 mb-3">
          🧠 ChatGPT 정리 코칭
        </h4>
        <p className="whitespace-pre-line text-gray-800">
          {aiAdvice || "정리 조언을 불러오는 중..."}
        </p>
      </div>

      {/* 기존 분석 피드백 */}
      <div className="flex-1 text-gray-700 text-lg leading-relaxed mb-6 overflow-auto whitespace-pre-line">
        {feedback || "AI가 분석한 결과가 여기에 표시됩니다."}
      </div>

      {/* 버튼 */}
      <div className="flex gap-4 justify-end">
        <button
          onClick={onButton1Click}
          className="px-10 py-3.5 bg-blue-500 text-white rounded-full hover:bg-blue-600 shadow-md"
        >
          다시 분석하기
        </button>
        <button
          onClick={onButton2Click}
          className="px-10 py-3.5 bg-green-500 text-white rounded-full hover:bg-green-600 shadow-md"
        >
          결과 저장
        </button>
      </div>
    </div>
  );
}
