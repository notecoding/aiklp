import React from "react";

/**
 * StepItem 컴포넌트
 * 서비스 이용 단계를 시각적으로 표현하는 개별 아이템
 *
 * @param {Object} props - 컴포넌트 속성
 * @param {React.ComponentType} props.icon - Lucide React 아이콘 컴포넌트
 * @param {string} props.label - 단계 설명 텍스트
 * @returns {JSX.Element} 단계 아이템 UI (아이콘 + 레이블)
 */
export function StepItem({ icon: Icon, label }) {
  return (
    <div className="flex flex-col items-center justify-center">
      {/* 원형 아이콘 컨테이너 */}
      <div className="flex items-center justify-center rounded-full shadow-sm bg-gray-200 p-2 w-16 h-16" href="/">
        <Icon size={60} className="text-gray-700" />
      </div>

      {/* 단계 설명 텍스트 */}
      <div className="py-4">{label}</div>
    </div>
  );
}