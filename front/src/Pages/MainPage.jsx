import React from "react";
import { AnalysisButton } from "../Components/AnalysisButton";
import { ImgBox } from "../Components/ImgBox";
import { ImgUpload } from "../Components/ImgUpload";
import { StepsSection } from "../Components/StepsSection";

export function MainPage() {
  return (
    <div className="bg-sky-100 h-screen">
      {/* 상단 문구 */}
      <div className="text-5xl font-bold pl-24 pt-12">
        어질러진 공간, <br />AI가 깔끔하게 정리해 드립니다.
      </div>

      {/* 중앙 영역 */}
      <div>
        <div className="flex items-center justify-center gap-8 py-12">
          <ImgUpload />
          <ImgBox />
          <ImgBox />
        </div>

        <div className="flex items-center justify-center pb-12">
          <AnalysisButton text="분석 시작" />
        </div>
      </div>

    
     
        <StepsSection />
    
    </div>
  );
}
