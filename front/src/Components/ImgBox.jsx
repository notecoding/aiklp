import React from "react";
import { Image } from "lucide-react";

/**
 * ImgBox 컴포넌트
 * 이미지를 표시하는 박스 (이미지가 없을 경우 플레이스홀더 표시)
 *
 * @param {Object} props - 컴포넌트 속성
 * @param {string} [props.src] - 표시할 이미지 URL
 * @param {string} [props.alt="예시 이미지"] - 이미지 대체 텍스트
 * @param {number} [props.width=420] - 박스의 너비 (px)
 * @param {number} [props.height=320] - 박스의 높이 (px)
 * @returns {JSX.Element} 이미지 박스 UI
 */
export function ImgBox({
  src,
  alt = "예시 이미지",
  width = 420,
  height = 320,
}) {
  return (
    <div
      className="flex items-center justify-center rounded-lg border border-gray-300 bg-gray-50 shadow-md overflow-hidden"
      style={{ width: `${width}px`, height: `${height}px` }}
    >
      {src ? (
        // 이미지가 있을 경우 표시
        <img src={src} alt={alt} className="w-full h-full object-cover" />
      ) : (
        // 이미지가 없을 경우 플레이스홀더 표시
        <div className="flex flex-col items-center gap-3">
          <Image size={48} className="text-gray-300" />
          <span className="text-gray-400 font-medium select-none">
            예시 이미지
          </span>
        </div>
      )}
    </div>
  );
}