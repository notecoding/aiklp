import React, { createContext, useContext, useState } from "react";

// 이미지 상태를 전역으로 관리하는 Context
const ImageContext = createContext();

/**
 * ImageProvider 컴포넌트
 * 앱 전체에서 이미지 업로드 상태를 공유
 */
export function ImageProvider({ children }) {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  return (
    <ImageContext.Provider
      value={{
        uploadedImage,
        setUploadedImage,
        imageFile,
        setImageFile,
        analysisResult,
        setAnalysisResult,
      }}
    >
      {children}
    </ImageContext.Provider>
  );
}

/**
 * useImage Hook
 * 이미지 Context를 사용하기 위한 커스텀 훅
 */
export function useImage() {
  const context = useContext(ImageContext);
  if (!context) {
    throw new Error("useImage must be used within ImageProvider");
  }
  return context;
}