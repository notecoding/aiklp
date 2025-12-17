// src/Pages/AnalysisPage.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useImage } from "../ImageContext";
import { AnalysisBox } from "../Components/AnalysisBox";
import { HeatmapToggle } from "../Components/HeatmapToggle";
import { ScoreBox } from "../Components/ScoreBox";
import { downloadImage } from "../utils/ImageDownload";

export function AnalysisPage() {
  const navigate = useNavigate();
  const { analysisResult } = useImage();
  const [activeView, setActiveView] = useState("normal"); // 🔥 뷰 전환

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

  const { data } = analysisResult;
  const {
    score,
    maxScore,
    feedback,
    aiAdvice,
    analyzedImage,
    heatmapImage,
    //improvedImage,
    segmentation, // 🔥 추가
    stacking, // 🔥 추가
    tracking, // 🔥 추가
  } = data;

  // 🔥 사용 가능한 이미지들
  const availableViews = {
    normal: analyzedImage,
    heatmap: heatmapImage,
    zones: segmentation?.zoneImage,
    stacks: stacking?.stackingImage,
  };

  return (
    <div className="bg-sky-100 min-h-screen">
      <div className="text-5xl font-bold pl-24 pt-12">
        어질러진 공간, <br />
        AI가 해결책을 제시합니다.
      </div>

      <div className="flex flex-row justify-center items-stretch gap-12 pt-16">
        {/* 왼쪽: 이미지 + 점수 */}
        <div className="flex flex-col gap-12">
          {/* 🔥 이미지 뷰어 (다중 뷰) */}
          <div className="flex flex-col gap-4">
            {/* 이미지 표시 영역 */}
            <div className="w-[550px] h-[400px] bg-gray-200 rounded-2xl overflow-hidden flex items-center justify-center">
              {availableViews[activeView] ? (
                <img
                  src={availableViews[activeView]}
                  alt={activeView}
                  className="max-w-full max-h-full object-contain"
                />
              ) : (
                <span className="text-gray-400 text-lg font-medium">
                  이미지를 불러올 수 없습니다
                </span>
              )}
            </div>

            {/* 🔥 뷰 선택 버튼들 */}
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setActiveView("normal")}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeView === "normal"
                    ? "bg-blue-500 text-white shadow-md"
                    : "bg-gray-200 text-gray-600 hover:bg-gray-300"
                }`}
              >
                📷 기본 분석
              </button>

              {heatmapImage && (
                <button
                  onClick={() => setActiveView("heatmap")}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    activeView === "heatmap"
                      ? "bg-red-500 text-white shadow-md"
                      : "bg-gray-200 text-gray-600 hover:bg-gray-300"
                  }`}
                >
                  🔥 히트맵
                </button>
              )}

              {segmentation?.zoneImage && (
                <button
                  onClick={() => setActiveView("zones")}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    activeView === "zones"
                      ? "bg-green-500 text-white shadow-md"
                      : "bg-gray-200 text-gray-600 hover:bg-gray-300"
                  }`}
                >
                  📍 구역 분석
                </button>
              )}

              {stacking?.stackingImage && (
                <button
                  onClick={() => setActiveView("stacks")}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    activeView === "stacks"
                      ? "bg-orange-500 text-white shadow-md"
                      : "bg-gray-200 text-gray-600 hover:bg-gray-300"
                  }`}
                >
                  📦 쌓임 감지
                </button>
              )}
            </div>

            {/* 현재 뷰 설명 */}
            <div className="bg-white rounded-lg p-3 text-sm text-gray-700">
              {activeView === "normal" && (
                <>
                  <strong>기본 분석:</strong> 감지된 물건과 위치 정보를
                  표시합니다.
                </>
              )}
              {activeView === "heatmap" && (
                <>
                  <strong>히트맵:</strong> 정리가 필요한 구역을 색상으로
                  표시합니다.
                </>
              )}
              {activeView === "zones" && (
                <>
                  <strong>구역 분석:</strong> Segmentation으로
                  바닥/침대/책상을 구분합니다.
                </>
              )}
              {activeView === "stacks" && (
                <>
                  <strong>쌓임 감지:</strong> 쌓이거나 포개진 물건 그룹을
                  표시합니다.
                </>
              )}
            </div>
          </div>

          {/* 점수 박스 */}
          <ScoreBox score={score} maxScore={maxScore} />
        </div>

        {/* 오른쪽: 분석 박스 */}
        <div className="h-full mb-20">
          <AnalysisBox
            feedback={feedback}
            aiAdvice={aiAdvice}
            //improvedImage={improvedImage}
            stackingData={stacking} // 🔥 추가
            trackingData={tracking} // 🔥 추가
            onButton1Click={() => navigate("/")}
            /*onButton2Click={() => {
              if (improvedImage) {
                downloadImage(improvedImage, `정리된_공간_${Date.now()}.jpg`);
              } else {
                alert("저장할 이미지가 없습니다.");
              }
            }}*/
          />
        </div>
      </div>
    </div>
  );
}
