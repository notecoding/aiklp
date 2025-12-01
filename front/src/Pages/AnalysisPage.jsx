import React from "react";
import { useNavigate } from "react-router-dom";
import { useImage } from "../ImageContext";
import { AnalysisBox } from "../Components/AnalysisBox";
import { HeatmapToggle } from "../Components/HeatmapToggle";
import { ScoreBox } from "../Components/ScoreBox";
import { downloadImage } from "../utils/ImageDownload";


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

  const { success, message, data } = analysisResult;
  //-------------------------------------//
  // 테스트용
  /*const mock = {
  success: true,
  message: "mock",
  data: {
    score: 78,
    maxScore: 100,
    feedback: "방이 조금 어질러져 있어요!",
    aiAdvice: "정리함에 물건을 넣어보세요.",
    analyzedImage: "/example.jpg",
    heatmapImage: "/example_heat.jpg",
    improvedImage: "/example_improved.jpg"
  }
};

const result = analysisResult ?? mock;

const { success, message, data } = result;*/
  //------------------------------------//
  const {
    score,
    maxScore,
    feedback,
    aiAdvice,
    analyzedImage,
    heatmapImage,
    improvedImage,
  } = data;

  return (
    <div className="bg-sky-100 min-h-screen">
      <div className="text-5xl font-bold pl-24 pt-12">
        어질러진 공간, <br />
        AI가 해결책을 제시합니다.
      </div>

      <div className="flex flex-row justify-center items-stretch gap-12 pt-16">
        <div className="flex flex-col flex-row gap-12">
          <HeatmapToggle
            normalImage={analyzedImage}
            heatmapImage={heatmapImage}
          />
          <ScoreBox score={score} maxScore={maxScore} />
        </div>
        <div className="h-full mb-20">
          <AnalysisBox
            feedback={feedback}
            aiAdvice={aiAdvice}
            improvedImage={improvedImage}
            onButton1Click={() => navigate("/")}
            onButton2Click={() => {
              if (improvedImage) {
                downloadImage(improvedImage, `정리된_공간_${Date.now()}.jpg`);
              } else {
                alert("저장할 이미지가 없습니다.");
              }
            }}
          />
        </div>
      </div>
    </div>
  );
}
