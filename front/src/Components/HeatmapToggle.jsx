import React, { useState } from "react";
import { Flame, Image as ImageIcon, Info } from "lucide-react";

/**
 * HeatmapToggle 컴포넌트 (범례 포함)
 * 일반 분석 이미지와 히트맵을 토글하여 표시
 * 히트맵 모드에서는 색상 범례 표시
 * 
 * @param {Object} props
 * @param {string} props.normalImage - 일반 분석 이미지 URL
 * @param {string} props.heatmapImage - 히트맵 이미지 URL
 * @returns {JSX.Element}
 */
export function HeatmapToggle({ normalImage, heatmapImage }) {
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showLegend, setShowLegend] = useState(true);
  
  // 히트맵이 없으면 일반 이미지만 표시
  if (!heatmapImage) {
    return (
      <div className="flex w-[550px] h-[400px] bg-gray-200 rounded-2xl flex items-center justify-center overflow-hidden shadow-md">
        {normalImage ? (
          <img
            src={normalImage}
            alt="분석 이미지"
            className="rounded-2xl max-w-full h-auto object-contain"
          />
        ) : (
          <span className="text-gray-400 text-lg font-medium">이미지</span>
        )}
      </div>
    );
  }
  
  return (
    <div className="flex flex-col gap-4">
      {/* 이미지 영역 */}
      <div className="relative flex w-[550px] h-[400px] bg-gray-200 rounded-2xl items-center justify-center overflow-hidden shadow-md">
        <img
          src={showHeatmap ? heatmapImage : normalImage}
          alt={showHeatmap ? "히트맵" : "분석 이미지"}
          className="rounded-2xl max-w-full h-auto object-contain"
        />
        
        {/* 히트맵 범례 (히트맵 모드일 때만 표시) */}
        {showHeatmap && showLegend && (
          <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Info size={16} className="text-blue-500" />
              <h4 className="font-bold text-sm text-gray-800">정리 필요도</h4>
            </div>
            
            <div className="space-y-2">
              {/* 빨강 */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-4 rounded bg-gradient-to-r from-red-600 to-red-500 border border-red-700"></div>
                <span className="text-xs text-gray-700 font-medium">매우 높음</span>
              </div>
              
              {/* 주황 */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-4 rounded bg-gradient-to-r from-orange-500 to-orange-400 border border-orange-600"></div>
                <span className="text-xs text-gray-700 font-medium">높음</span>
              </div>
              
              {/* 노랑 */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-4 rounded bg-gradient-to-r from-yellow-400 to-yellow-300 border border-yellow-500"></div>
                <span className="text-xs text-gray-700 font-medium">보통</span>
              </div>
              
              {/* 초록 */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-4 rounded bg-gradient-to-r from-green-400 to-green-300 border border-green-500"></div>
                <span className="text-xs text-gray-700 font-medium">낮음</span>
              </div>
              
              {/* 파랑 */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-4 rounded bg-gradient-to-r from-blue-400 to-blue-300 border border-blue-500"></div>
                <span className="text-xs text-gray-700 font-medium">매우 낮음</span>
              </div>
            </div>
            
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-500 leading-relaxed">
                <span className="text-red-600 font-semibold">빨간색</span>: 바닥에 있는 물건<br />
                <span className="text-blue-600 font-semibold">파란색</span>: 정리된 물건
              </p>
            </div>
            
            {/* 범례 닫기 버튼 */}
            <button
              onClick={() => setShowLegend(false)}
              className="mt-2 w-full text-xs text-gray-500 hover:text-gray-700 underline"
            >
              범례 숨기기
            </button>
          </div>
        )}
        
        {/* 범례 다시 보기 버튼 (숨겼을 때) */}
        {showHeatmap && !showLegend && (
          <button
            onClick={() => setShowLegend(true)}
            className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-md p-2 hover:bg-white transition-colors"
            title="범례 보기"
          >
            <Info size={20} className="text-blue-500" />
          </button>
        )}
      </div>
      
      {/* 토글 버튼 */}
      <div className="flex gap-2 justify-center">
        <button
          onClick={() => setShowHeatmap(false)}
          className={`px-6 py-2 rounded-lg flex items-center gap-2 transition-all ${
            !showHeatmap
              ? 'bg-blue-500 text-white shadow-md'
              : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
          }`}
        >
          <ImageIcon size={18} />
          <span>일반 보기</span>
        </button>
        
        <button
          onClick={() => {
            setShowHeatmap(true);
            setShowLegend(true); // 히트맵 켤 때 범례도 자동으로 표시
          }}
          className={`px-6 py-2 rounded-lg flex items-center gap-2 transition-all ${
            showHeatmap
              ? 'bg-red-500 text-white shadow-md'
              : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
          }`}
        >
          <Flame size={18} />
          <span>히트맵</span>
        </button>
      </div>
      
      {/* 히트맵 설명 */}
      {showHeatmap && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Flame size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold text-sm text-red-800 mb-1">히트맵 안내</h4>
              <p className="text-xs text-red-700 leading-relaxed">
                색상이 <span className="font-bold">빨간색</span>에 가까울수록 <span className="font-bold">정리가 시급한 구역</span>입니다. 
                특히 바닥에 있는 물건이 빨갛게 표시됩니다.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}