import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import StudentDashboard from "./pages/StudentDashboard";
import ResearcherDashboard from "./pages/ResearcherDashboard";
import PublicDashboard from "./pages/PublicDashboard";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<Login />} />

        <Route
          path="/student"
          element={<StudentDashboard />}
        />

        <Route path="/researcher" element={<ResearcherDashboard />} />
        <Route path="/public" element={<PublicDashboard />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;