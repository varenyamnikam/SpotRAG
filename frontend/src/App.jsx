import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import TopicsPage from "./components/TopicsPage";
import LecturesPage from "./components/LecturesPage";
import "./App.css";
import "./index.css";
import "./styles.css";

const App = () => {
  return (
    <Router>
      <div className="app-wrapper">
        <Routes>
          <Route path="/" element={<TopicsPage />} />
          <Route path="/lectures/:topicId" element={<LecturesPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
