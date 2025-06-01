import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import AiAssistant from './components/Aiassistant'; 
import Meetings from './components/Meetings';
import 'react-big-calendar/lib/css/react-big-calendar.css'; 

function App() {
  return (
    <Router>
      <div
        style={{
          minHeight: "100vh",
          background: "linear-gradient(to right, #f8f9fa, #e9ecef)",
          fontFamily: "Inter, system-ui, -apple-system, sans-serif",
          color: "#333",
        }}
      >
        {/* Navbar */}
        <nav
          style={{
            background: "white",
            padding: "16px 30px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            position: "sticky",
            top: 0,
            zIndex: 100,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
            }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ color: "#6366f1" }}
            >
              <path d="M12 20h9"></path>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
            <h1
              style={{
                color: "#6366f1",
                margin: 0,
                fontSize: "22px",
                fontWeight: 700,
              }}
            >
              Task Dashboard
            </h1>
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "20px",
            }}
          >
            <Link to="/ai-assistant" style={{ textDecoration: "none" }}>
              <button
                style={{
                  background: "#10b981",
                  color: "white",
                  border: "none",
                  padding: "8px 16px",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "14px",
                  fontWeight: 500,
                  transition: "all 0.2s ease",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
                onMouseOver={(e) => (e.target.style.background = "#059669")}
                onMouseOut={(e) => (e.target.style.background = "#10b981")}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                AI Assistant
              </button>
            </Link>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
              }}
            >
              <div
                style={{
                  width: "36px",
                  height: "36px",
                  borderRadius: "50%",
                  background: "#6366f1",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "white",
                  fontWeight: "bold",
                  fontSize: "16px",
                }}
              >
                S
              </div>
              <span
                style={{
                  color: "#4b5563",
                  fontWeight: 500,
                }}
              >
                Welcome, Shreya!
              </span>
            </div>
            <button
              style={{
                background: "#ef4444",
                color: "white",
                border: "none",
                padding: "8px 16px",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: 500,
                transition: "all 0.2s ease",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
              onMouseOver={(e) => (e.target.style.background = "#dc2626")}
              onMouseOut={(e) => (e.target.style.background = "#ef4444")}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="15"
                height="15"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
            </button>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/ai-assistant" element={<AiAssistant />} />
          <Route path="/meetings" element={<Meetings />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;