import React from "react";
import { useNavigate } from "react-router-dom";
import { useImage } from "../ImageContext";
import { ScoreBox } from "../Components/ScoreBox";
import { AnalysisBox } from "../Components/AnalysisBox";
import { HeatmapToggle } from "../Components/HeatmapToggle";

export function AnalysisPage() {
  const navigate = useNavigate();
  const { analysisResult, uploadedImage } = useImage();

  if (!analysisResult) {
    return (
      <div className="bg-sky-100 h-screen flex flex-col items-center justify-center">
        <div className="bg-white rounded-2xl shadow-lg p-12 max-w-md text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            분석 결과가 없습니다
          </h2>
          <p className="text-gray-600 mb-6">
            먼저 이미지를 업로드하고 분석을 시작해주세요.
          </p>
          <button
            onClick={() => navigate("/")}
            className="bg-blue-500 text-white px-8 py-3 rounded-lg hover:bg-blue-600 transition-colors font-semibold shadow-md"
          >
            메인 페이지로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  const {
    success = false,
    message = "분석 실패",
    data = {}
  } = analysisResult;

  const {
    score = 0,
    maxScore = 100,
    feedback = "",
    analyzedImage = uploadedImage,
    heatmapImage = null  // 🔥 히트맵 이미지 추가
  } = data;

  if (!success) {
    return (
      <div className="bg-sky-100 h-screen flex flex-col items-center justify-center">
        <div className="bg-white rounded-2xl shadow-lg p-12 max-w-md text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">
            분석 실패 😥
          </h2>
          <p className="text-gray-600 mb-6">
            {message || "AI 분석 중 오류가 발생했습니다."}
          </p>
          <button
            onClick={() => navigate("/")}
            className="bg-blue-500 text-white px-8 py-3 rounded-lg hover:bg-blue-600 transition-colors font-semibold shadow-md"
          >
            다시 시도하기
          </button>
        </div>
      </div>
    );
  }

  const handleButton1Click = () => navigate("/");
  const handleButton2Click = () => {
    alert("결과를 저장했습니다!");
  };

  return (
    <div className="bg-sky-100 min-h-screen">
      <div className="text-5xl font-bold pl-24 pt-12">
        어질러진 공간, <br />
        AI가 깔끔하게 정리해 드립니다.
      </div>

      <div className="flex justify-center items-start gap-12 pt-24">
        <div className="flex flex-col gap-12">
          {/* 🔥 히트맵 토글로 교체 */}
          <div className="flex flex-col gap-6">
            <HeatmapToggle 
              normalImage={analyzedImage}
              heatmapImage={heatmapImage}
            />
            
            {/* 점수 박스 */}
            <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-2xl px-8 py-6 shadow-md border-2 border-gray-200">
              <div className="text-center">
                <p className="text-gray-700 text-base mb-2">최종 점수</p>
                <div className="flex items-center justify-center gap-3">
                  <span className={`font-bold text-4xl ${
                    score >= 90 ? 'text-green-600' :
                    score >= 70 ? 'text-blue-600' :
                    score >= 50 ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {score}점
                  </span>
                  <span className="text-gray-400 text-lg">/ {maxScore}점</span>
                </div>
                <p className={`text-lg font-semibold mt-3 ${
                  score >= 90 ? 'text-green-600' :
                  score >= 70 ? 'text-blue-600' :
                  score >= 50 ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {score >= 90 ? '🟢 매우 깨끗' :
                   score >= 70 ? '🔵 깨끗함' :
                   score >= 50 ? '🟡 보통' :
                   '🔴 정리 필요'}
                </p>
              </div>
            </div>
          </div>
        </div>

        <AnalysisBox
          feedback={feedback}
          onButton1Click={handleButton1Click}
          onButton2Click={handleButton2Click}
        />
      </div>
    </div>
  );
}