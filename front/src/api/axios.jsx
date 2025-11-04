// src/api/axios.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000", // Flask 서버 주소
  withCredentials: true, // 쿠키/세션 필요할 때
});

export default api;
