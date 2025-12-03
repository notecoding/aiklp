// src/Components/StackingWarning.jsx
import React, { useState } from "react";
import { Layers, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";

/**
 * 쌓임/포개짐 경고 컴포넌트
 * - 수직 쌓임: 책, 박스 등이 쌓인 경우
 * - 포개짐: 옷, 서류 등이 포개진 경우
 */
export function StackingWarning({ stacks, stackingImage }) {
  const [expanded, setExpanded] = useState(true);

  if (!stacks || stacks.length === 0) return null;

  const highSeverity = stacks.filter((s) => s.severity === "high");

  return (
    <div className="bg-orange-50 border-2 border-orange-300 rounded-xl p-5 mb-4">
      {/* 헤더 */}
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <Layers size={24} className="text-orange-600" />
          <h4 className="text-lg font-bold text-orange-800">
            📦 쌓임/포개짐 감지: {stacks.length}개
            {highSeverity.length > 0 && ` (위험: ${highSeverity.length})`}
          </h4>
        </div>
        {expanded ? (
          <ChevronUp className="text-orange-600" />
        ) : (
          <ChevronDown className="text-orange-600" />
        )}
      </div>

      {/* 내용 */}
      {expanded && (
        <div className="mt-4 space-y-3">
          {stacks.map((stack, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg ${
                stack.severity === "high"
                  ? "bg-red-50 border border-red-300"
                  : "bg-yellow-50 border border-yellow-300"
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  {stack.severity === "high" && (
                    <AlertTriangle
                      size={16}
                      className="text-red-600 inline mr-2"
                    />
                  )}
                  <span className="font-bold">{stack.message}</span>
                  <div className="text-sm text-gray-600 mt-1">
                    {stack.type === "vertical_stack"
                      ? "⚠️ 수직으로 쌓여 넘어질 위험이 있습니다"
                      : "📚 포개져있어 찾기 어렵습니다"}
                  </div>
                </div>
                <div
                  className={`px-3 py-1 rounded-full text-sm font-bold ${
                    stack.severity === "high"
                      ? "bg-red-200 text-red-800"
                      : "bg-yellow-200 text-yellow-800"
                  }`}
                >
                  {stack.count}개
                </div>
              </div>
            </div>
          ))}

          {/* 쌓임 시각화 이미지 */}
          {stackingImage && (
            <div className="mt-3">
              <p className="text-sm text-gray-600 mb-2">쌓임 시각화:</p>
              <img
                src={stackingImage}
                alt="쌓임 시각화"
                className="rounded-lg w-full border border-orange-200"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
