/**
 * 이미지를 다운로드하는 유틸리티 함수
 * @param {string} imageUrl - 다운로드할 이미지 URL
 * @param {string} filename - 저장할 파일명 (기본값: improved_image.jpg)
 */
export async function downloadImage(imageUrl, filename = "improved_image.jpg") {
  try {
    // CORS 문제를 피하기 위해 fetch로 이미지 가져오기
    const response = await fetch(imageUrl);
    const blob = await response.blob();

    // Blob을 URL로 변환
    const blobUrl = window.URL.createObjectURL(blob);

    // 임시 a 태그 생성
    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = filename;

    // 다운로드 트리거
    document.body.appendChild(link);
    link.click();

    // 정리
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);

    return true;
  } catch (error) {
    console.error("이미지 다운로드 실패:", error);
    alert("이미지 다운로드에 실패했습니다.");
    return false;
  }
}
