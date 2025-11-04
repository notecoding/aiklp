import React from "react";
import { Loader2 } from "lucide-react";

/**
 * LoadingModal 컴포넌트
 * AI 분석 진행 중 표시되는 팝업
 * 
 * @param {Object} props - 컴포넌트 속성
 * @param {boolean} props.isOpen - 모달 표시 여부
 * @param {string} [props.message="AI가 이미지를 분석하고 있습니다..."] - 표시할 메시지
 * @returns {JSX.Element|null} 로딩 모달 UI
 */
export function LoadingModal({ isOpen, message = "AI가 이미지를 분석하고 있습니다..." }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 shadow-2xl flex flex-col items-center gap-4 max-w-md">
        {/* 회전하는 로더 아이콘 */}
        <Loader2 size={64} className="text-blue-500 animate-spin" />
        
        {/* 메시지 */}
        <p className="text-lg font-medium text-gray-700 text-center">
          {message}
        </p>
        
        {/* 부가 설명 */}
        <p className="text-sm text-gray-500 text-center">
          잠시만 기다려주세요
        </p>
      </div>
    </div>
  );
}