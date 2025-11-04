import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useImage } from "../ImageContext";
import { uploadAndAnalyzeImage } from "../api/ImageApi";
import { LoadingModal } from "./LoadingModal";

/**
 * AnalysisButton 컴포넌트
 * 이미지 분석을 시작하는 버튼
 * 클릭 시 이미지를 백엔드로 전송하고 분석 완료 후 결과 페이지로 이동
 * 
 * @param {Object} props - 컴포넌트 속성
 * @param {string} props.text - 버튼에 표시할 텍스트
 * @returns {JSX.Element} 분석 버튼 UI
 */
export  function AnalysisButton({ text }) {
  const navigate = useNavigate();
  const { imageFile, setAnalysisResult } = useImage();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * 분석 시작 핸들러
   * 이미지를 백엔드로 전송하고 분석 완료 후 결과 페이지로 이동
   */
  const handleAnalysis = async () => {
    // 이미지가 업로드되지 않은 경우
    if (!imageFile) {
      alert("먼저 이미지를 업로드해주세요.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // 백엔드로 이미지 전송 및 분석 요청
      const result = await uploadAndAnalyzeImage(imageFile);
      
      // 분석 결과를 Context에 저장
      setAnalysisResult(result);

      // 분석 완료 후 결과 페이지로 이동
      navigate("/analysis");
    } catch (err) {
      // 에러 처리
      setError(err.message);
      alert(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <button
        className="analysis-button bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors font-semibold shadow-md disabled:bg-gray-400 disabled:cursor-not-allowed"
        onClick={handleAnalysis}
        disabled={isLoading || !imageFile}
      >
        {text}
      </button>

      {/* 로딩 모달 */}
      <LoadingModal isOpen={isLoading} />
    </>
  );
}