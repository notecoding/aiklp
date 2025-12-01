import api from "./axios.jsx";

/**
 * 이미지를 서버에 업로드하고 AI 분석을 요청
 * 히트맵 + ChatGPT 정리 조언(ai_advice) 포함
 *
 * @param {File} imageFile - 업로드할 이미지 파일
 * @returns {Promise<Object>}
 */
export async function uploadAndAnalyzeImage(imageFile) {
  try {
    // FormData 생성
    const formData = new FormData();
    formData.append("image", imageFile);

    // 서버로 업로드 + 분석 요청
    const response = await api.post("/analyze", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      withCredentials: true,
    });

    const backendData = response.data;

    // 🔥 서버 응답 로그 (정상 위치로 이동)
    console.log("🔥 서버 응답:", backendData);

    // 프론트에서 사용할 형식으로 변환
    const transformedData = {
      success: backendData.status === "success",
      message: "분석이 완료되었습니다.",
      data: {
        // 점수
        score: backendData.report?.score || 0,
        maxScore: 100,

        // 🔥 ChatGPT 분석 조언 추가
        aiAdvice: backendData.ai_advice || "",

        // 기존 분석 요약
        feedback: generateFeedback(backendData),

        // 이미지 URL
        analyzedImage: backendData.result_image
          ? `http://localhost:5000${backendData.result_image}`
          : null,

        // 히트맵 URL
        heatmapImage: backendData.heatmap_image
          ? `http://localhost:5000${backendData.heatmap_image}`
          : null,
        // 개선된 이미지 URL (AI가 생성한 정리된 이미지)
        improvedImage: backendData.improved_image
          ? `http://localhost:5000${backendData.improved_image}`
          : null,

        // 기타 데이터
        detections: backendData.detections || [],
        issues: backendData.report?.issues || [],
        suggestions: backendData.report?.suggestions || [],
      },
    };

    return transformedData;
  } catch (error) {
    console.error("이미지 분석 중 오류 발생:", error);
    throw new Error(
      error.response?.data?.message || "이미지 분석에 실패했습니다."
    );
  }
}

/**
 * 기존 간결한 분석 결과 생성 함수
 */
function generateFeedback(backendData) {
  const { report } = backendData;

  if (!report) {
    return "분석 결과를 생성할 수 없습니다.";
  }

  let feedback = "";

  const score = report.score || 0;

  if (score >= 90) feedback += "✨ 매우 깔끔하게 정리되어 있습니다!\n\n";
  else if (score >= 70) feedback += "👍 전반적으로 잘 정리되어 있습니다.\n\n";
  else if (score >= 50) feedback += "⚠️ 정리가 필요한 부분이 있습니다.\n\n";
  else feedback += "❗ 공간이 많이 어질러져 있습니다.\n\n";

  feedback += `📊 정리 점수: ${score}점 / 100점\n\n`;

  if (report.issues?.length) {
    feedback += "🔍 발견된 문제:\n";
    report.issues.forEach((issue, index) => {
      feedback += `  ${index + 1}. ${issue}\n`;
    });
    feedback += "\n";
  }

  if (report.suggestions?.length) {
    feedback += "💡 개선 제안:\n";
    report.suggestions.forEach((suggestion, index) => {
      feedback += `  ${index + 1}. ${suggestion}\n`;
    });
  }

  return feedback.trim();
}

/**
 * 분석 기록 조회
 */
export async function getAnalysisHistory(limit = 10) {
  try {
    const response = await api.get(`/history?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error("히스토리 조회 중 오류 발생:", error);
    throw new Error("히스토리를 가져오는데 실패했습니다.");
  }
}

/**
 * 통계 조회
 */
export async function getStatistics() {
  try {
    const response = await api.get("/statistics");
    return response.data;
  } catch (error) {
    console.error("통계 조회 중 오류 발생:", error);
    throw new Error("통계를 가져오는데 실패했습니다.");
  }
}
