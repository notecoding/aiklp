import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MainPage } from './Pages/MainPage';
import { AnalysisPage } from './Pages/AnalysisPage';
import './App.css';
import { TopBar } from './Components/TopBar';
import { ImageProvider } from './ImageContext';

function App() {
  return (
    <ImageProvider>
        <Router>
          {/* 상단 바 */}
          <TopBar />

          {/* 메인 콘텐츠 (남은 영역 전부 차지) */}
          <div className="flex-1 overflow-hidden">
            <Routes>
              <Route path="/" element={<MainPage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
            </Routes>
          </div>
        </Router>
    </ImageProvider>
  );
}

export default App;