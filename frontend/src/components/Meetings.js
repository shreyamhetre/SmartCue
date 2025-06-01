import React, { useState, useEffect } from "react";
import { Calendar, momentLocalizer } from "react-big-calendar";
import moment from "moment";
import { useLocation, useNavigate } from "react-router-dom";

const localizer = momentLocalizer(moment);

const Meetings = () => {
  const [meetings, setMeetings] = useState([]);
  const [error, setError] = useState(null);
  const [view, setView] = useState("month"); 
  const [date, setDate] = useState(new Date()); 
  const location = useLocation();
  const navigate = useNavigate();

  const queryParams = new URLSearchParams(location.search);
  const taskId = queryParams.get("taskId");

  const fetchMeetings = () => {
    fetch("http://localhost:8000/meetings")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch meetings");
        }
        return response.json();
      })
      .then((data) => {
        setMeetings(data.meetings);
        setError(null);
      })
      .catch((error) => {
        console.error("Error fetching meetings:", error);
        setError("Failed to load meetings. Please try again later.");
      });
  };

  useEffect(() => {
    fetchMeetings();

    if (taskId && meetings.length > 0) {
      const meeting = meetings.find((m) => m.id === parseInt(taskId));
      if (meeting) {
        setDate(new Date(meeting.meeting_datetime));
      }
    }
  }, [taskId, meetings.length]); 

  const events = meetings.map((meeting) => ({
    id: meeting.id,
    title: meeting.task_name,
    start: new Date(meeting.meeting_datetime),
    end: new Date(new Date(meeting.meeting_datetime).getTime() + 60 * 60 * 1000), 
    allDay: false,
    resource: meeting,
  }));

  const eventStyleGetter = (event) => {
    const isHighlighted = taskId && event.id === parseInt(taskId);
    return {
      style: {
        backgroundColor: isHighlighted ? "#10b981" : "#6366f1",
        borderRadius: "4px",
        opacity: 0.8,
        color: "white",
        border: "none",
        fontSize: "14px",
        fontWeight: "500",
      },
    };
  };

  const customTooltipAccessor = (event) => {
    const meeting = event.resource;
    return (
      `Task: ${meeting.task_name}\n` +
      `Description: ${meeting.meeting_description}\n` +
      `Assignees: ${meeting.assignee_for_meeting}\n` +
      `Time: ${new Date(meeting.meeting_datetime).toLocaleString()}`
    );
  };

  const handleViewChange = (newView) => {
    setView(newView);
  };

  const handleNavigate = (action) => {
    const newDate = new Date(date);
    if (action === "TODAY") {
      setDate(new Date()); // Set to today (May 22, 2025)
    } else if (action === "PREV") {
      if (view === "month") {
        newDate.setMonth(newDate.getMonth() - 1);
      } else if (view === "week") {
        newDate.setDate(newDate.getDate() - 7);
      } else if (view === "day") {
        newDate.setDate(newDate.getDate() - 1);
      }
      setDate(newDate);
    } else if (action === "NEXT") {
      if (view === "month") {
        newDate.setMonth(newDate.getMonth() + 1);
      } else if (view === "week") {
        newDate.setDate(newDate.getDate() + 7);
      } else if (view === "day") {
        newDate.setDate(newDate.getDate() + 1);
      }
      setDate(newDate);
    }
  };

  const handleMonthChange = (e) => {
    const selectedMonth = parseInt(e.target.value); // Month index (0-11)
    const newDate = new Date(date);
    newDate.setMonth(selectedMonth);
    newDate.setFullYear(2025); // Hardcode to 2025
    setDate(newDate);
  };

  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];

  const CustomToolbar = ({ label, onNavigate, onView }) => {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "10px 20px",
          borderBottom: "1px solid #e5e7eb",
          background: "#f9fafb",
        }}
      >
        {/* Navigation Buttons */}
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            onClick={() => handleNavigate("TODAY")}
            style={{
              background: "#6366f1",
              color: "white",
              border: "none",
              padding: "6px 12px",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "500",
              transition: "background 0.2s",
            }}
            onMouseOver={(e) => (e.target.style.background = "#4f46e5")}
            onMouseOut={(e) => (e.target.style.background = "#6366f1")}
          >
            Today
          </button>
          <button
            onClick={() => handleNavigate("PREV")}
            style={{
              background: "white",
              color: "#4b5563",
              border: "1px solid #d1d5db",
              padding: "6px 12px",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "500",
              transition: "all 0.2s ease",
            }}
            onMouseOver={(e) => {
              e.target.style.background = "#f9fafb";
              e.target.style.borderColor = "#9ca3af";
            }}
            onMouseOut={(e) => {
              e.target.style.background = "white";
              e.target.style.borderColor = "#d1d5db";
            }}
          >
            Back
          </button>
          <button
            onClick={() => handleNavigate("NEXT")}
            style={{
              background: "white",
              color: "#4b5563",
              border: "1px solid #d1d5db",
              padding: "6px 12px",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "500",
              transition: "all 0.2s ease",
            }}
            onMouseOver={(e) => {
              e.target.style.background = "#f9fafb";
              e.target.style.borderColor = "#9ca3af";
            }}
            onMouseOut={(e) => {
              e.target.style.background = "white";
              e.target.style.borderColor = "#d1d5db";
            }}
          >
            Next
          </button>
          {/* Month Dropdown */}
          <select
            value={date.getMonth()}
            onChange={handleMonthChange}
            style={{
              padding: "6px 12px",
              border: "1px solid #d1d5db",
              borderRadius: "4px",
              fontSize: "14px",
              background: "white",
              color: "#111827",
              fontWeight: "500",
              marginLeft: "10px",
            }}
          >
            {months.map((month, index) => (
              <option key={month} value={index}>
                {month} 2025
              </option>
            ))}
          </select>
        </div>

        {/* View Switcher */}
        <div style={{ display: "flex", gap: "10px" }}>
          {["month", "week", "day"].map((viewName) => (
            <button
              key={viewName}
              onClick={() => onView(viewName)}
              style={{
                padding: "6px 12px",
                border: "none",
                borderRadius: "4px",
                background: view === viewName ? "white" : "transparent",
                color: view === viewName ? "#111827" : "#6b7280",
                fontSize: "14px",
                fontWeight: "500",
                cursor: "pointer",
                boxShadow: view === viewName ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
                transition: "all 0.2s",
              }}
            >
              {viewName.charAt(0).toUpperCase() + viewName.slice(1)}
            </button>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div
      style={{
        padding: "30px",
        maxWidth: "1200px",
        margin: "0 auto",
        fontFamily: "Inter, system-ui, -apple-system, sans-serif",
        color: "#333",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "30px",
        }}
      >
        <div>
          <h2
            style={{
              fontSize: "24px",
              fontWeight: "700",
              color: "#111827",
              margin: "0 0 8px 0",
            }}
          >
            Meeting Calendar
          </h2>
          <p
            style={{
              fontSize: "14px",
              color: "#6b7280",
              margin: 0,
            }}
          >
            View and manage your scheduled meetings
          </p>
        </div>
        <button
          onClick={() => navigate("/")}
          style={{
            background: "#6366f1",
            color: "white",
            border: "none",
            padding: "10px 20px",
            borderRadius: "6px",
            cursor: "pointer",
            fontSize: "14px",
            fontWeight: "500",
            transition: "all 0.2s ease",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          }}
          onMouseOver={(e) => (e.target.style.background = "#4f46e5")}
          onMouseOut={(e) => (e.target.style.background = "#6366f1")}
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
            <path d="M15 18l-6-6 6-6"></path>
          </svg>
          Back to Dashboard
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div
          style={{
            background: "#fef2f2",
            color: "#b91c1c",
            border: "1px solid #ef4444",
            padding: "12px 16px",
            borderRadius: "6px",
            marginBottom: "20px",
            fontSize: "14px",
          }}
        >
          {error}
        </div>
      )}

      {/* Calendar */}
      <div
        style={{
          background: "white",
          borderRadius: "8px",
          padding: "20px",
          boxShadow: "0 4px 6px rgba(0,0,0,0.05)",
          border: "1px solid #e5e7eb",
          height: "600px",
        }}
      >
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{
            height: "100%",
            fontFamily: "Inter, system-ui, -apple-system, sans-serif",
          }}
          eventPropGetter={eventStyleGetter}
          tooltipAccessor={customTooltipAccessor}
          view={view}
          onView={handleViewChange}
          date={date} // Control the date dynamically
          onNavigate={(newDate) => setDate(newDate)} // Update date on navigation
          components={{
            toolbar: CustomToolbar,
          }}
          views={["month", "week", "day"]}
          step={60}
          timeslots={1}
        />
      </div>
    </div>
  );
};

export default Meetings;