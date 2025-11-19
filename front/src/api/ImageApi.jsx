import api from "./axios.jsx";

/**
 * 이미지를 서버에 업로드하고 AI 분석을 요청
 * 히트맵 이미지도 함께 수신
 * 
 * @param {File} imageFile - 업로드할 이미지 파일
 * @returns {Promise<Object>} 프론트엔드 형식으로 변환된 서버 응답 데이터
 * @throws {Error} 업로드 또는 분석 실패 시
 */
export async function uploadAndAnalyzeImage(imageFile) {
  try {
    // FormData 객체 생성
    const formData = new FormData();
    formData.append("image", imageFile);

    // 서버에 이미지 업로드 및 분석 요청
    const response = await api.post("/analyze", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      withCredentials: true,
    });

    // 백엔드 응답 구조:
    // {
    //   "status": "success",
    //   "detections": [...],
    //   "report": {
    //     "score": 72,
    //     "issues": ["chair", "book"],
    //     "suggestions": [...]
    //   },
    //   "result_image": "/results/test_image.jpg",
    //   "heatmap_image": "/results/heatmap_test_image.jpg"
    // }
    
    const backendData = response.data;
    
    // 프론트엔드가 기대하는 형식으로 변환
    const transformedData = {
      success: backendData.status === "success",
      message: "분석이 완료되었습니다.",
      data: {
        // 점수
        score: backendData.report?.score || 0,
        maxScore: 100,
        
        // 피드백 텍스트 생성 (간결한 버전)
        feedback: generateFeedback(backendData),
        
        // 결과 이미지 URL
        analyzedImage: backendData.result_image 
          ? `http://localhost:5000${backendData.result_image}`
          : null,
        
        // 히트맵 이미지 URL
        heatmapImage: backendData.heatmap_image
          ? `http://localhost:5000${backendData.heatmap_image}`
          : null,
        
        // 추가 정보
        detections: backendData.detections || [],
        issues: backendData.report?.issues || [],
        suggestions: backendData.report?.suggestions || []
      }
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
 * 백엔드 응답을 사용자 친화적인 피드백 텍스트로 변환
 * ✅ 상세 리포트 제거 - 간결한 버전만 표시
 * 
 * @param {Object} backendData - 백엔드 응답 데이터
 * @returns {string} 포맷된 피드백 텍스트
 */
function generateFeedback(backendData) {
  const { report } = backendData;
  
  if (!report) {
    return "분석 결과를 생성할 수 없습니다.";
  }
  
  let feedback = "";
  
  // 점수에 따른 전체 평가
  const score = report.score || 0;
  if (score >= 90) {
    feedback += "✨ 매우 깔끔하게 정리되어 있습니다!\n\n";
  } else if (score >= 70) {
    feedback += "👍 전반적으로 잘 정리되어 있습니다.\n\n";
  } else if (score >= 50) {
    feedback += "⚠️ 정리가 필요한 부분이 있습니다.\n\n";
  } else {
    feedback += "❗ 공간이 많이 어질러져 있습니다.\n\n";
  }
  
  feedback += `📊 정리 점수: ${score}점 / 100점\n\n`;
  
  // 발견된 문제점
  if (report.issues && report.issues.length > 0) {
    feedback += "🔍 발견된 문제:\n";
    report.issues.forEach((issue, index) => {
      feedback += `  ${index + 1}. ${issue}\n`;
    });
    feedback += "\n";
  }
  
  // 개선 제안
  if (report.suggestions && report.suggestions.length > 0) {
    feedback += "💡 개선 제안:\n";
    report.suggestions.forEach((suggestion, index) => {
      feedback += `  ${index + 1}. ${suggestion}\n`;
    });
  }
  
  // ✅ detailed_report 부분 완전 제거!
  
  return feedback.trim();
}

/**
 * 분석 기록 조회
 * 
 * @param {number} limit - 조회할 최대 개수
 * @returns {Promise<Array>} 분석 기록 리스트
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
 * 
 * @returns {Promise<Object>} 통계 데이터
 */
export async function getStatistics() {
  try {
    const response = await api.get('/statistics');
    return response.data;
  } catch (error) {
    console.error("통계 조회 중 오류 발생:", error);
    throw new Error("통계를 가져오는데 실패했습니다.");
  }
}