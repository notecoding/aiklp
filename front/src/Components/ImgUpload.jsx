import React, { useState, useEffect } from "react";
import { Upload } from "lucide-react";
import { useImage } from "../ImageContext";

/**
 * ImgUpload 컴포넌트
 * 사용자가 이미지를 업로드할 수 있는 드래그 앤 드롭 영역
 * 업로드된 이미지는 미리보기로 표시되고 Context에 저장됨
 *
 * @param {Object} props - 컴포넌트 속성
 * @param {number} [props.width=420] - 업로드 영역의 너비 (px)
 * @param {number} [props.height=320] - 업로드 영역의 높이 (px)
 * @returns {JSX.Element} 이미지 업로드 UI
 */
export function ImgUpload({ width = 420, height = 320 }) {
  // Context에서 이미지 상태 가져오기
  const { uploadedImage, setUploadedImage, setImageFile } = useImage();
  
  // 로컬 미리보기 URL 상태
  const [preview, setPreview] = useState(uploadedImage);

  // Context의 uploadedImage가 변경되면 preview도 업데이트
  useEffect(() => {
    setPreview(uploadedImage);
  }, [uploadedImage]);

  /**
   * 파일 선택 시 미리보기 URL 생성 및 Context에 저장
   * @param {React.ChangeEvent<HTMLInputElement>} e - 파일 입력 이벤트
   */
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const previewUrl = URL.createObjectURL(file);
      setPreview(previewUrl);
      setUploadedImage(previewUrl);
      setImageFile(file); // 실제 파일 객체 저장
    }
  };

  return (
    <div
      className="flex items-center justify-center"
      style={{ width: `${width}px`, height: `${height}px` }}
    >
      <label className="w-full h-full border-2 border-dashed border-gray-400 flex flex-col items-center justify-center cursor-pointer rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors shadow-md overflow-hidden">
        {/* 숨겨진 파일 입력 필드 */}
        <input
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleFileChange}
        />

        {preview ? (
          // 업로드된 이미지 미리보기
          <img
            src={preview}
            alt="업로드된 이미지"
            className="w-full h-full object-cover"
          />
        ) : (
          // 기본 업로드 안내 UI
          <div className="flex flex-col items-center gap-3">
            <Upload size={48} className="text-gray-400" />
            <span className="text-gray-500 font-medium select-none">
              이미지 업로드
            </span>
          </div>
        )}
      </label>
    </div>
  );
}