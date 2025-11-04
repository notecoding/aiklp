import React from "react";
import { useNavigate } from "react-router-dom";
import { useImage } from "../ImageContext";
import { ScoreBox } from "../Components/ScoreBox";
import { AnalysisBox } from "../Components/AnalysisBox";

/**
 * AnalysisPage 컴포넌트
 * AI 분석 결과를 표시하는 페이지
 * - 백엔드에서 받은 이미지, 점수, 피드백을 화면에 표시
 */
export function AnalysisPage() {
  const navigate = useNavigate();
  const { analysisResult, uploadedImage } = useImage();

  // 분석 결과가 없으면 메인 페이지로 돌아가도록 안내
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

  // 백엔드 응답에서 데이터 추출
  // 백엔드 응답 형식: { success, message, data: { score, feedback, analyzedImage } }
  const {
    score = 0,
    maxScore = 100,
    feedback = "AI 분석 결과입니다.",
    analyzedImage = null, // 백엔드가 처리한 이미지 (있을 경우)
  } = analysisResult.data || analysisResult;

  // 표시할 이미지: 백엔드가 반환한 이미지 우선, 없으면 업로드한 원본 이미지 사용
  const displayImage = analyzedImage || uploadedImage;

  /**
   * 버튼 1 클릭 핸들러 - 다시 분석하기
   */
  const handleButton1Click = () => {
    navigate("/");
  };

  /**
   * 버튼 2 클릭 핸들러 - 결과 저장
   */
  const handleButton2Click = () => {
    console.log("분석 결과:", analysisResult);
    alert("결과를 저장했습니다!");
  };

  return (
    <div className="bg-sky-100 h-screen">
      {/* 상단 문구 */}
      <div className="text-5xl font-bold pl-24 pt-12">
        어질러진 공간, <br />
        AI가 깔끔하게 정리해 드립니다.
      </div>

      {/* 결과 표시 영역 */}
      <div className="flex justify-center items-center gap-12 pt-24">
        {/* 왼쪽: 이미지 + 점수 */}
        <div className="flex flex-col gap-12">
          <ScoreBox
            imageSrc={displayImage}
            score={score}
            maxScore={maxScore}
          />
        </div>

        {/* 오른쪽: 분석 결과 텍스트 + 버튼 */}
        <AnalysisBox
          feedback={feedback}
          onButton1Click={handleButton1Click}
          onButton2Click={handleButton2Click}
        />
      </div>
    </div>
  );
}