import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

const Dashboard = () => {
  const [showForm, setShowForm] = useState(false);
  const [tasks, setTasks] = useState([]);
  const [viewMode, setViewMode] = useState("open");
  const [selectedAssignee, setSelectedAssignee] = useState("");
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1); // State for pagination

  const navigate = useNavigate();

  // Create an array of unique assignees from tasks
  const uniqueAssignees = useMemo(() => {
    const assignees = tasks
      .map(task => task.assignee)
      .filter(Boolean)
      .filter((assignee, index, self) => self.indexOf(assignee) === index)
      .sort();
    return assignees;
  }, [tasks]);

  const [formData, setFormData] = useState({
    task_name: "",
    description: "",
    priority: "high",
    assignee: "",
    meeting_description: "",
    assignee_for_meeting: "",
    meeting_date: "",
    meeting_time: "",
  });

  // Fetch tasks from API and poll for updates
  const fetchTasks = () => {
    fetch('http://localhost:8000/tasks')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch tasks');
        }
        return response.json();
      })
      .then((data) => setTasks(data.tasks))
      .catch((error) => console.error('Error fetching tasks:', error));
  };

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Submitting task:", formData);

    // Send the new task to the API
    fetch('http://localhost:8000/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        task_name: formData.task_name,
        description: formData.description,
        priority: formData.priority,
        assignee: formData.assignee,
        meeting_description: formData.meeting_description || undefined,
        assignee_for_meeting: formData.assignee_for_meeting || undefined,
        meeting_date: formData.meeting_date || undefined,
        meeting_time: formData.meeting_time || undefined,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to create task');
        }
        return response.json();
      })
      .then((newTask) => {
        fetchTasks();
        setShowForm(false);
        setFormData({
          task_name: "",
          description: "",
          priority: "high",
          assignee: "",
          meeting_description: "",
          assignee_for_meeting: "",
          meeting_date: "",
          meeting_time: "",
        });
        setSnackbarOpen(true);
      })
      .catch((error) => console.error('Error creating task:', error));
  };

  // Filter tasks based on viewMode and selected assignee
  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      const matchesViewMode = viewMode === "open"
        ? task.status === "open"
        : ["completed", "notplanned"].includes(task.status);
      
      const matchesAssignee = !selectedAssignee || task.assignee === selectedAssignee;
      
      return matchesViewMode && matchesAssignee;
    });
  }, [tasks, viewMode, selectedAssignee]);

  // Pagination logic
  const tasksPerPage = 10;
  const totalPages = Math.ceil(filteredTasks.length / tasksPerPage);
  const paginatedTasks = filteredTasks.slice((currentPage - 1) * tasksPerPage, currentPage * tasksPerPage);

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  // Helper function to get status badge style
  const getStatusStyle = (status) => {
    switch (status) {
      case "open":
        return {
          background: "#ecfdf5",
          color: "#047857",
          border: "1px solid #10b981",
          padding: "4px 8px",
          borderRadius: "12px",
          fontSize: "12px",
          fontWeight: "500",
          display: "inline-block",
        };
      case "notplanned":
        return {
          background: "#eff6ff",
          color: "#1d4ed8",
          border: "1px solid #3b82f6",
          padding: "4px 8px",
          borderRadius: "12px",
          fontSize: "12px",
          fontWeight: "500",
          display: "inline-block",
        };
      case "completed":
        return {
          background: "#f3f4f6",
          color: "#4b5563",
          border: "1px solid #9ca3af",
          padding: "4px 8px",
          borderRadius: "12px",
          fontSize: "12px",
          fontWeight: "500",
          display: "inline-block",
        };
      default:
        return {};
    }
  };

  // Helper function to get priority badge style
  const getPriorityStyle = (priority) => {
    switch (priority) {
      case "high":
        return {
          background: "#fef2f2",
          color: "#b91c1c",
          border: "1px solid #ef4444",
          padding: "4px 8px",
          borderRadius: "12px",
          fontSize: "12px",
          fontWeight: "500",
          display: "inline-block",
        };
      case "medium":
        return {
          background: "#fffbeb",
          color: "#b45309",
          border: "1px solid #f59e0b",
          padding: "4px 8px",
          borderRadius: "12px",
          fontSize: "12px",
          fontWeight: "500",
          display: "inline-block",
        };
      case "low":
        return {
          background: "#f0f9ff",
          color: "#0369a1",
          border: "1px solid #0ea5e9",
          padding: "4px 8px",
          borderRadius: "12px",
          fontSize: "12px",
          fontWeight: "500",
          display: "inline-block",
        };
      default:
        return {};
    }
  };

  return (
    <div
      style={{
        padding: "30px",
        maxWidth: "1200px",
        margin: "0 auto",
      }}
    >
      {/* Dashboard Header */}
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
            Task Management
          </h2>
          <p
            style={{
              fontSize: "14px",
              color: "#6b7280",
              margin: 0,
            }}
          >
            Manage and track your team's tasks efficiently
          </p>
        </div>

        {/* Add Task Button */}
        <button
          onClick={() => setShowForm(true)}
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
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Add New Task
        </button>
      </div>

      {/* Tasks Summary Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
          gap: "20px",
          marginBottom: "30px",
        }}
      >
        <div
          style={{
            background: "white",
            borderRadius: "8px",
            padding: "20px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
            border: "1px solid #e5e7eb",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "10px",
            }}
          >
            <h3 style={{ margin: 0, fontSize: "16px", color: "#4b5563" }}>Total Tasks</h3>
            <div
              style={{
                background: "#f3f4f6",
                borderRadius: "50%",
                width: "40px",
                height: "40px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{ color: "#6366f1" }}
              >
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
          </div>
          <p
            style={{
              fontSize: "28px",
              fontWeight: "700",
              margin: "0",
              color: "#111827",
            }}
          >
            {tasks.length}
          </p>
        </div>

        {/* Assignee Card */}
        <div
          style={{
            background: "white",
            borderRadius: "8px",
            padding: "20px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
            border: "1px solid #e5e7eb",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "10px",
            }}
          >
            <h3 style={{ margin: 0, fontSize: "16px", color: "#4b5563" }}>Assignees</h3>
            <div
              style={{
                background: "#f0f9ff",
                borderRadius: "50%",
                width: "40px",
                height: "40px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{ color: "#0ea5e9" }}
              >
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
            </div>
          </div>
          <p
            style={{
              fontSize: "28px",
              fontWeight: "700",
              margin: "0",
              color: "#111827",
            }}
          >
            {uniqueAssignees.length}
          </p>
        </div>

        <div
          style={{
            background: "white",
            borderRadius: "8px",
            padding: "20px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
            border: "1px solid #e5e7eb",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "10px",
            }}
          >
            <h3 style={{ margin: 0, fontSize: "16px", color: "#4b5563" }}>Completed</h3>
            <div
              style={{
                background: "#ecfdf5",
                borderRadius: "50%",
                width: "40px",
                height: "40px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{ color: "#10b981" }}
              >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
          </div>
          <p
            style={{
              fontSize: "28px",
              fontWeight: "700",
              margin: "0",
              color: "#111827",
            }}
          >
            {tasks.filter((task) => task.status === "completed").length}
          </p>
        </div>

        <div
          style={{
            background: "white",
            borderRadius: "8px",
            padding: "20px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
            border: "1px solid #e5e7eb",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "10px",
            }}
          >
            <h3 style={{ margin: 0, fontSize: "16px", color: "#4b5563" }}>High Priority</h3>
            <div
              style={{
                background: "#fef2f2",
                borderRadius: "50%",
                width: "40px",
                height: "40px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{ color: "#ef4444" }}
              >
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
          </div>
          <p
            style={{
              fontSize: "28px",
              fontWeight: "700",
              margin: "0",
              color: "#111827",
            }}
          >
            {tasks.filter((task) => task.priority === "high").length}
          </p>
        </div>
      </div>

      {/* Tasks Table */}
      <div
        style={{
          background: "white",
          borderRadius: "8px",
          overflow: "hidden",
          boxShadow: "0 4px 6px rgba(0,0,0,0.05)",
          border: "1px solid #e5e7eb",
        }}
      >
        <div
          style={{
            padding: "16px 20px",
            borderBottom: "1px solid #e5e7eb",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h3
            style={{
              margin: 0,
              fontSize: "18px",
              fontWeight: "600",
              color: "#111827",
            }}
          >
            {viewMode === "open" ? "Open Tasks" : "Closed Tasks"}
          </h3>
          <div
            style={{
              display: "flex",
              gap: "10px",
              alignItems: "center",
            }}
          >
            {/* Toggle Button */}
            <div
              style={{
                display: "flex",
                background: "#f3f4f6",
                borderRadius: "6px",
                padding: "2px",
              }}
            >
              <button
                onClick={() => setViewMode("open")}
                style={{
                  padding: "6px 12px",
                  border: "none",
                  borderRadius: "4px",
                  background: viewMode === "open" ? "white" : "transparent",
                  color: viewMode === "open" ? "#111827" : "#6b7280",
                  fontSize: "14px",
                  fontWeight: "500",
                  cursor: "pointer",
                  boxShadow: viewMode === "open" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
                  transition: "all 0.2s",
                }}
              >
                Open
              </button>
              <button
                onClick={() => setViewMode("closed")}
                style={{
                  padding: "6px 12px",
                  border: "none",
                  borderRadius: "4px",
                  background: viewMode === "closed" ? "white" : "transparent",
                  color: viewMode === "closed" ? "#111827" : "#6b7280",
                  fontSize: "14px",
                  fontWeight: "500",
                  cursor: "pointer",
                  boxShadow: viewMode === "closed" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
                  transition: "all 0.2s",
                }}
              >
                Closed
              </button>
            </div>

            {/* Search Bar */}
            <div
              style={{
                position: "relative",
                display: "flex",
                alignItems: "center",
              }}
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
                style={{
                  position: "absolute",
                  left: "10px",
                  color: "#9ca3af",
                }}
              >
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <input
                type="text"
                placeholder="Search tasks..."
                style={{
                  padding: "8px 8px 8px 32px",
                  border: "1px solid #e5e7eb",
                  borderRadius: "6px",
                  fontSize: "14px",
                  width: "200px",
                }}
              />
            </div>

            {/* Filter by Assignee Dropdown */}
            <select
              value={selectedAssignee}
              onChange={(e) => setSelectedAssignee(e.target.value)}
              style={{
                padding: "8px 12px",
                border: "1px solid #e5e7eb",
                borderRadius: "6px",
                fontSize: "14px",
                background: "white",
                minWidth: "200px",
              }}
            >
              <option value="">All Assignees</option>
              <option value="">Unassigned</option>
              {uniqueAssignees.map((assignee) => (
                <option key={assignee} value={assignee}>
                  {assignee}
                </option>
              ))}
            </select>
          </div>
        </div>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
          }}
        >
          <thead>
            <tr
              style={{
                background: "#f9fafb",
                borderBottom: "1px solid #e5e7eb",
              }}
            >
              <th
                style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#4b5563",
                }}
              >
                ID
              </th>
              <th
                style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#4b5563",
                }}
              >
                Task Name
              </th>
              <th
                style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#4b5563",
                }}
              >
                Description
              </th>
              <th
                style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#4b5563",
                }}
              >
                Status
              </th>
              <th
                style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#4b5563",
                }}
              >
                Priority
              </th>
              <th
                style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#4b5563",
                }}
              >
                Assignee
              </th>
              <th
                style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#4b5563",
                }}
              >
                Meeting
              </th>
              <th
                style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#4b5563",
                }}
              >
                GitHub Issue
              </th>
              <th
                style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#4b5563",
                }}
              >
                Created At
              </th>
              <th
                style={{
                  padding: "12px 16px",
                  textAlign: "center",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#4b5563",
                }}
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedTasks.map((task) => (
              <tr
                key={task.id}
                style={{
                  borderBottom: "1px solid #e5e7eb",
                  transition: "background-color 0.2s",
                }}
                onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "#f9fafb")}
                onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
              >
                <td
                  style={{
                    padding: "16px",
                    fontSize: "14px",
                    color: "#6b7280",
                  }}
                >
                  {task.id}
                </td>
                <td
                  style={{
                    padding: "16px",
                    fontSize: "14px",
                    fontWeight: "500",
                    color: "#111827",
                  }}
                >
                  {task.task_name}
                </td>
                <td
                  style={{
                    padding: "16px",
                    fontSize: "14px",
                    color: "#4b5563",
                    maxWidth: "200px",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {task.description}
                </td>
                <td style={{ padding: "16px" }}>
                  <span style={getStatusStyle(task.status)}>
                    {task.status === "open" ? "Open" : task.status === "notplanned" ? "Not Planned" : "Completed"}
                  </span>
                </td>
                <td style={{ padding: "16px" }}>
                  <span style={getPriorityStyle(task.priority)}>
                    {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                  </span>
                </td>
                <td
                  style={{
                    padding: "16px",
                    fontSize: "14px",
                    color: "#4b5563",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                    }}
                  >
                    <div
                      style={{
                        width: "28px",
                        height: "28px",
                        borderRadius: "50%",
                        background: "#6366f1",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "white",
                        fontWeight: "bold",
                        fontSize: "12px",
                      }}
                    >
                      {task.assignee
                        ? task.assignee
                            .split(" ")
                            .map((name) => name[0])
                            .join("")
                        : "U"}
                    </div>
                    {task.assignee || "Unassigned"}
                  </div>
                </td>
                <td
                  style={{
                    padding: "16px",
                    fontSize: "14px",
                    color: "#4b5563",
                  }}
                >
                  {task.meeting_datetime
                    ? new Date(task.meeting_datetime).toLocaleString()
                    : "No Meeting"}
                </td>
                <td style={{ padding: "16px" }}>
                  <a
                    href={task.github_issue_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      color: "#6366f1",
                      textDecoration: "none",
                      fontSize: "14px",
                      fontWeight: "500",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
                    </svg>
                    View Issue
                  </a>
                </td>
                <td
                  style={{
                    padding: "16px",
                    fontSize: "14px",
                    color: "#6b7280",
                  }}
                >
                  {new Date(task.created_at).toLocaleDateString()}
                </td>
                <td
                  style={{
                    padding: "16px",
                    textAlign: "center",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "center",
                      gap: "8px",
                    }}
                  >
                    {task.meeting_datetime && (
                      <button
                        onClick={() => navigate(`/meetings?taskId=${task.id}`)}
                        style={{
                          background: "#f3f4f6",
                          border: "none",
                          borderRadius: "4px",
                          padding: "6px",
                          cursor: "pointer",
                        }}
                        title="View Meeting"
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
                          style={{ color: "#10b981" }}
                        >
                          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                          <line x1="16" y1="2" x2="16" y2="6"></line>
                          <line x1="8" y1="2" x2="8" y2="6"></line>
                          <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {paginatedTasks.length === 0 && (
              <tr>
                <td
                  colSpan={10}
                  style={{
                    padding: "40px 16px",
                    textAlign: "center",
                    color: "#6b7280",
                    fontSize: "14px",
                  }}
                >
                  No tasks found. Create a new task to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {/* Pagination Controls */}
{/* Pagination Controls */}
{filteredTasks.length > 0 && (
  <div
    style={{
      display: "flex",
      justifyContent: "flex-end", // Align to the right
      alignItems: "center",
      padding: "16px 20px",
      borderTop: "1px solid #e5e7eb",
      gap: "10px", // Space between elements
    }}
  >
    <button
      onClick={handlePreviousPage}
      disabled={currentPage === 1}
      style={{
        background: currentPage === 1 ? "#d1d5db" : "#6366f1",
        color: "white",
        border: "none",
        padding: "8px", // Reduced padding for icon-only button
        borderRadius: "6px",
        cursor: currentPage === 1 ? "not-allowed" : "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: "32px", // Fixed width for icon button
        height: "32px", // Fixed height for icon button
        transition: "background 0.2s",
        opacity: currentPage === 1 ? 0.5 : 1,
      }}
      onMouseOver={(e) => {
        if (currentPage !== 1) e.target.style.background = "#4f46e5";
      }}
      onMouseOut={(e) => {
        if (currentPage !== 1) e.target.style.background = "#6366f1";
      }}
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
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </button>
    <span
      style={{
        fontSize: "14px",
        color: "#4b5563",
      }}
    >
      Page {currentPage} of {totalPages}
    </span>
    <button
      onClick={handleNextPage}
      disabled={currentPage === totalPages}
      style={{
        background: currentPage === totalPages ? "#d1d5db" : "#6366f1",
        color: "white",
        border: "none",
        padding: "8px", // Reduced padding for icon-only button
        borderRadius: "6px",
        cursor: currentPage === totalPages ? "not-allowed" : "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: "32px", // Fixed width for icon button
        height: "32px", // Fixed height for icon button
        transition: "background 0.2s",
        opacity: currentPage === totalPages ? 0.5 : 1,
      }}
      onMouseOver={(e) => {
        if (currentPage !== totalPages) e.target.style.background = "#4f46e5";
      }}
      onMouseOut={(e) => {
        if (currentPage !== totalPages) e.target.style.background = "#6366f1";
      }}
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
        <polyline points="9 18 15 12 9 6"></polyline>
      </svg>
    </button>
  </div>
)}
      </div>

      {/* Form Popup */}
      {showForm && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 1000,
            backdropFilter: "blur(4px)",
          }}
        >
          <form
            onSubmit={handleSubmit}
            style={{
              background: "white",
              padding: "30px",
              borderRadius: "12px",
              width: "500px",
              maxWidth: "90%",
              boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
              maxHeight: "90vh",
              overflowY: "auto",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "24px",
              }}
            >
              <h2
                style={{
                  margin: 0,
                  color: "#111827",
                  fontSize: "20px",
                  fontWeight: "600",
                }}
              >
                Create New Task
              </h2>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "#6b7280",
                  padding: "4px",
                }}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label
                style={{
                  display: "block",
                  marginBottom: "6px",
                  color: "#4b5563",
                  fontSize: "14px",
                  fontWeight: "500",
                }}
              >
                Task Name
              </label>
              <input
                type="text"
                name="task_name"
                value={formData.task_name}
                onChange={handleInputChange}
                required
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  border: "1px solid #d1d5db",
                  borderRadius: "6px",
                  fontSize: "14px",
                  transition: "border-color 0.2s",
                  outline: "none",
                }}
                onFocus={(e) => (e.target.style.borderColor = "#6366f1")}
                onBlur={(e) => (e.target.style.borderColor = "#d1d5db")}
                placeholder="Enter task name"
              />
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label
                style={{
                  display: "block",
                  marginBottom: "6px",
                  color: "#4b5563",
                  fontSize: "14px",
                  fontWeight: "500",
                }}
              >
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                required
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  border: "1px solid #d1d5db",
                  borderRadius: "6px",
                  fontSize: "14px",
                  minHeight: "100px",
                  resize: "vertical",
                  transition: "border-color 0.2s",
                  outline: "none",
                }}
                onFocus={(e) => (e.target.style.borderColor = "#6366f1")}
                onBlur={(e) => (e.target.style.borderColor = "#d1d5db")}
                placeholder="Enter task description"
              />
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr",
                gap: "16px",
                marginBottom: "20px",
              }}
            >
              <div>
                <label
                  style={{
                    display: "block",
                    marginBottom: "6px",
                    color: "#4b5563",
                    fontSize: "14px",
                    fontWeight: "500",
                  }}
                >
                  Priority
                </label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleInputChange}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px",
                    background: "white",
                    transition: "border-color 0.2s",
                    outline: "none",
                  }}
                  onFocus={(e) => (e.target.style.borderColor = "#6366f1")}
                  onBlur={(e) => (e.target.style.borderColor = "#d1d5db")}
                >
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label
                style={{
                  display: "block",
                  marginBottom: "6px",
                  color: "#4b5563",
                  fontSize: "14px",
                  fontWeight: "500",
                }}
              >
                Assignee
              </label>
              <input
                type="text"
                name="assignee"
                value={formData.assignee}
                onChange={handleInputChange}
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  border: "1px solid #d1d5db",
                  borderRadius: "6px",
                  fontSize: "14px",
                  transition: "border-color 0.2s",
                  outline: "none",
                }}
                onFocus={(e) => (e.target.style.borderColor = "#6366f1")}
                onBlur={(e) => (e.target.style.borderColor = "#d1d5db")}
                placeholder="Enter assignee name"
              />
            </div>

            {/* Meeting Fields */}
            <div style={{ marginBottom: "20px" }}>
              <label
                style={{
                  display: "block",
                  marginBottom: "6px",
                  color: "#4b5563",
                  fontSize: "14px",
                  fontWeight: "500",
                }}
              >
                Meeting Description (Optional)
              </label>
              <textarea
                name="meeting_description"
                value={formData.meeting_description}
                onChange={handleInputChange}
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  border: "1px solid #d1d5db",
                  borderRadius: "6px",
                  fontSize: "14px",
                  minHeight: "80px",
                  resize: "vertical",
                  transition: "border-color 0.2s",
                  outline: "none",
                }}
                onFocus={(e) => (e.target.style.borderColor = "#6366f1")}
                onBlur={(e) => (e.target.style.borderColor = "#d1d5db")}
                placeholder="Enter meeting description"
              />
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label
                style={{
                  display: "block",
                  marginBottom: "6px",
                  color: "#4b5563",
                  fontSize: "14px",
                  fontWeight: "500",
                }}
              >
                Meeting Assignees (Optional, comma-separated)
              </label>
              <input
                type="text"
                name="assignee_for_meeting"
                value={formData.assignee_for_meeting}
                onChange={handleInputChange}
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  border: "1px solid #d1d5db",
                  borderRadius: "6px",
                  fontSize: "14px",
                  transition: "border-color 0.2s",
                  outline: "none",
                }}
                onFocus={(e) => (e.target.style.borderColor = "#6366f1")}
                onBlur={(e) => (e.target.style.borderColor = "#d1d5db")}
                placeholder="e.g., shreyamhetre,john"
              />
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "16px",
                marginBottom: "20px",
              }}
            >
              <div>
                <label
                  style={{
                    display: "block",
                    marginBottom: "6px",
                    color: "#4b5563",
                    fontSize: "14px",
                    fontWeight: "500",
                  }}
                >
                  Meeting Date (Optional)
                </label>
                <input
                  type="date"
                  name="meeting_date"
                  value={formData.meeting_date}
                  onChange={handleInputChange}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px",
                    transition: "border-color 0.2s",
                    outline: "none",
                  }}
                  onFocus={(e) => (e.target.style.borderColor = "#6366f1")}
                  onBlur={(e) => (e.target.style.borderColor = "#d1d5db")}
                />
              </div>
              <div>
                <label
                  style={{
                    display: "block",
                    marginBottom: "6px",
                    color: "#4b5563",
                    fontSize: "14px",
                    fontWeight: "500",
                  }}
                >
                  Meeting Time (Optional)
                </label>
                <input
                  type="time"
                  name="meeting_time"
                  value={formData.meeting_time}
                  onChange={handleInputChange}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px",
                    transition: "border-color 0.2s",
                    outline: "none",
                  }}
                  onFocus={(e) => (e.target.style.borderColor = "#6366f1")}
                  onBlur={(e) => (e.target.style.borderColor = "#d1d5db")}
                />
              </div>
            </div>

            <div
              style={{
                display: "flex",
                gap: "12px",
                justifyContent: "flex-end",
              }}
            >
              <button
                type="button"
                onClick={() => setShowForm(false)}
                style={{
                  background: "white",
                  color: "#4b5563",
                  border: "1px solid #d1d5db",
                  padding: "10px 16px",
                  borderRadius: "6px",
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
                Cancel
              </button>
              <button
                type="submit"
                style={{
                  background: "#6366f1",
                  color: "white",
                  border: "none",
                  padding: "10px 20px",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "14px",
                  fontWeight: "500",
                  transition: "background 0.2s",
                }}
                onMouseOver={(e) => (e.target.style.background = "#4f46e5")}
                onMouseOut={(e) => (e.target.style.background = "#6366f1")}
              >
                Create Task
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Snackbar for success message */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity="success"
          sx={{ width: '100%' }}
        >
          Task created successfully!
        </Alert>
      </Snackbar>
    </div>
  );
};

export default Dashboard;