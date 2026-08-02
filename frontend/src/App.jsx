import { Routes, Route, NavLink } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import ProcessesPage from "./pages/ProcessesPage";
import VariablesPage from "./pages/VariablesPage";
import SamplesPage from "./pages/SamplesPage";
import ModelsPage from "./pages/ModelsPage";
import AlertsPage from "./pages/AlertsPage";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/processes", label: "Procesos" },
  { to: "/variables", label: "Variables" },
  { to: "/samples", label: "Muestras" },
  { to: "/models", label: "Modelos" },
  { to: "/alerts", label: "Alertas" },
];

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center gap-8">
          <span className="font-bold text-blue-600 text-lg">SPC System</span>
          <div className="flex gap-6">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `text-sm font-medium transition-colors ${
                    isActive
                      ? "text-blue-600 border-b-2 border-blue-600 pb-1"
                      : "text-gray-500 hover:text-gray-800"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/processes" element={<ProcessesPage />} />
          <Route path="/variables" element={<VariablesPage />} />
          <Route path="/samples" element={<SamplesPage />} />
          <Route path="/models" element={<ModelsPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
        </Routes>
      </main>
    </div>
  );
}