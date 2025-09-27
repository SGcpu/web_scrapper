// Main App component with routing
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Dashboard } from "./components/Dashboard.tsx";
import { ProductsPage } from "./components/ProductsPage.tsx";
import { ScrapingPage } from "./components/ScrapingPage.tsx";
import { AnalysisPage } from "./components/AnalysisPage.tsx";
import { Navigation } from "./components/common/Navigation.tsx";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/scraping" element={<ScrapingPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
