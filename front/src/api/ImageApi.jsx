// src/api/ImageApi.jsx
import api from "./axios.jsx";

/**
 * 이미지를 서버에 업로드하고 AI 분석을 요청
 * 🔥 3개 AI 개선사항 통합 버전
 */
export async function uploadAndAnalyzeImage(imageFile) {
  try {
    const formData = new FormData();
    formData.append("image", imageFile);

    const response = await api.post("/analyze", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      withCredentials: true,
    });

    const backendData = response.data;
    console.log("🔥 서버 응답 (완전 개선 버전):", backendData);

    // 프론트에서 사용할 형식으로 변환
    const transformedData = {
      success: backendData.status === "success",
      message: "분석이 완료되었습니다.",
      data: {
        // 점수
        score: backendData.report?.score || 0,
        maxScore: 100,

        // 🔥 ChatGPT 조언
        aiAdvice: backendData.ai_advice || "",

        // 기존 분석 요약
        feedback: generateFeedback(backendData),

        // 이미지들
        analyzedImage: backendData.result_image
          ? `http://localhost:5000${backendData.result_image}`
          : null,

        heatmapImage: backendData.heatmap_image
          ? `http://localhost:5000${backendData.heatmap_image}`
          : null,

        // 기존 improvedImage 유지
        improvedImage: backendData.improved_image
          ? `http://localhost:5000${backendData.improved_image}`
          : null,

        // 🔥 Segmentation 데이터
        segmentation: {
          zoneImage: backendData.segmentation?.zone_image
            ? `http://localhost:5000${backendData.segmentation.zone_image}`
            : null,
          areaCoverage: backendData.segmentation?.area_coverage || null,
          detectedAreas: backendData.segmentation?.detected_areas || [],
        },

        // 🔥 쌓임 데이터
        stacking: {
          stacks: backendData.stacking?.stacks || [],
          stackingImage: backendData.stacking?.stacking_image
            ? `http://localhost:5000${backendData.stacking.stacking_image}`
            : null,
          totalStacks: backendData.stacking?.total_stacks || 0,
        },

        // 🔥 추적 데이터
        tracking: {
          chronicProblems: backendData.tracking?.chronic_problems || [],
          statistics: backendData.tracking?.statistics || null,
        },

        // 기타
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
 * 간결한 분석 결과 생성
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
