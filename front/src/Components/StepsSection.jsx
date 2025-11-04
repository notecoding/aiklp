import React from "react";
import { Brain, Camera, ScrollText } from "lucide-react";
import { StepItem } from "./StepItem.jsx";

/**
 * 서비스 사용 단계 정보
 * 각 단계는 아이콘과 설명 레이블로 구성됨
 */
const STEPS = [
  { icon: Camera, label: "1. 사진 업로드" },
  { icon: Brain, label: "2. AI 진단" },
  { icon: ScrollText, label: "3. 맞춤형 정리 제공" },
];

/**
 * StepsSection 컴포넌트
 * 화면 하단에 서비스 이용 3단계를 안내하는 섹션
 * 카드형태로 각 단계를 시각적으로 표현
 *
 * @returns {JSX.Element} 3단계 안내 UI
 */
export function StepsSection() {
  return (
    <div className="w-full flex justify-center gap-52 py-8 bg-white">
      {STEPS.map((step, idx) => (
        <StepItem key={idx} icon={step.icon} label={step.label} />
      ))}
    </div>
  );
}