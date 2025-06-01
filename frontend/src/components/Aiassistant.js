// import { useState } from "react";
// import { Link } from "react-router-dom";
// import Snackbar from '@mui/material/Snackbar';
// import Alert from '@mui/material/Alert';
// import CircularProgress from '@mui/material/CircularProgress';

// const AiAssistant = () => {
//   const [prompt, setPrompt] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [snackbarOpen, setSnackbarOpen] = useState(false);
//   const [snackbarMessage, setSnackbarMessage] = useState("");
//   const [snackbarSeverity, setSnackbarSeverity] = useState("success");

//   // Example prompt suggestions
//   const suggestions = [
//     "Create a high-priority task to design a logo for the marketing team",
//     "Add a medium-priority task to write a report for John",
//     "Create a low-priority task to schedule a meeting with Sarah"
//   ];

//   // Simple prompt parsing (can be enhanced with NLP)
//   const parsePrompt = (prompt) => {
//     const taskData = {
//       task_name: "",
//       description: "",
//       priority: "medium", // Default
//       assignee: "",
//     };

//     const lowerPrompt = prompt.toLowerCase();
//     // Extract task name (between "task to" and "for" or end of string)
//     const taskMatch = prompt.match(/task to (.*?)(\sfor|$)/i);
//     if (taskMatch) {
//       taskData.task_name = taskMatch[1].trim();
//       taskData.description = taskMatch[1].trim(); // Use task name as description for simplicity
//     }

//     // Extract priority
//     if (lowerPrompt.includes("high-priority")) {
//       taskData.priority = "high";
//     } else if (lowerPrompt.includes("low-priority")) {
//       taskData.priority = "low";
//     }

//     // Extract assignee (after "for")
//     const assigneeMatch = prompt.match(/for (.*?)$/i);
//     if (assigneeMatch) {
//       taskData.assignee = assigneeMatch[1].trim();
//     }

//     return taskData;
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     if (!prompt.trim()) {
//       setSnackbarMessage("Please enter a prompt!");
//       setSnackbarSeverity("error");
//       setSnackbarOpen(true);
//       return;
//     }

//     setLoading(true);
//     const taskData = parsePrompt(prompt);

//     // Send the task to the API
//     fetch('http://localhost:8000/tasks', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//       },
//       body: JSON.stringify({
//         task_name: taskData.task_name || "Task from AI Assistant",
//         description: taskData.description || "Created via AI Assistant",
//         priority: taskData.priority,
//         assignee: taskData.assignee,
//       }),
//     })
//       .then((response) => {
//         if (!response.ok) {
//           throw new Error('Failed to create task');
//         }
//         return response.json();
//       })
//       .then(() => {
//         setLoading(false);
//         setSnackbarMessage("Task created successfully!");
//         setSnackbarSeverity("success");
//         setSnackbarOpen(true);
//         setPrompt(""); // Clear the prompt
//       })
//       .catch((error) => {
//         setLoading(false);
//         setSnackbarMessage("Error creating task: " + error.message);
//         setSnackbarSeverity("error");
//         setSnackbarOpen(true);
//         console.error('Error creating task:', error);
//       });
//   };

//   return (
//     <div
//       style={{
//         padding: "30px",
//         maxWidth: "1200px",
//         margin: "0 auto",
//       }}
//     >
//       {/* Header */}
//       <div
//         style={{
//           display: "flex",
//           justifyContent: "space-between",
//           alignItems: "center",
//           marginBottom: "30px",
//         }}
//       >
//         <div>
//           <h2
//             style={{
//               fontSize: "24px",
//               fontWeight: "700",
//               color: "#111827",
//               margin: "0 0 8px 0",
//             }}
//           >
//             AI Assistant
//           </h2>
//           <p
//             style={{
//               fontSize: "14px",
//               color: "#6b7280",
//               margin: 0,
//             }}
//           >
//             Create tasks using natural language prompts
//           </p>
//         </div>
//         <Link to="/"
//         style={{ textDecoration: "none" }} 
//          >
//           <button
//             style={{
//               background: "#6366f1",
//               color: "white",
//               border: "none",
//               padding: "10px 20px",
//               borderRadius: "6px",
//               cursor: "pointer",
//               fontSize: "14px",
//               fontWeight: "500",
//               transition: "all 0.2s ease",
//               display: "flex",
//               alignItems: "center",
//               gap: "8px",
//               boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
//             }}
//             onMouseOver={(e) => (e.target.style.background = "#4f46e5")}
//             onMouseOut={(e) => (e.target.style.background = "#6366f1")}
//           >
//             <svg
//               xmlns="http://www.w3.org/2000/svg"
//               width="16"
//               height="16"
//               viewBox="0 0 24 24"
//               fill="none"
//               stroke="currentColor"
//               strokeWidth="2"
//               strokeLinecap="round"
//               strokeLinejoin="round"
//             >
//               <path d="M19 12H5"></path>
//               <path d="M12 19l-7-7 7-7"></path>
//             </svg>
//             Back to Dashboard
//           </button>
//         </Link>
//       </div>

//       {/* Prompt Input Section */}
//       <div
//         style={{
//           background: "white",
//           borderRadius: "8px",
//           padding: "20px",
//           boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
//           border: "1px solid #e5e7eb",
//         }}
//       >
//         <form onSubmit={handleSubmit}>
//           <div style={{ marginBottom: "20px" }}>
//             <label
//               style={{
//                 display: "block",
//                 marginBottom: "6px",
//                 color: "#4b5563",
//                 fontSize: "14px",
//                 fontWeight: "500",
//               }}
//             >
//               Enter Your Prompt
//             </label>
//             <textarea
//               value={prompt}
//               onChange={(e) => setPrompt(e.target.value)}
//               placeholder="e.g., Create a high-priority task to design a logo for the marketing team"
//               style={{
//                 width: "100%",
//                 padding: "10px 12px",
//                 border: "1px solid #d1d5db",
//                 borderRadius: "6px",
//                 fontSize: "14px",
//                 minHeight: "120px",
//                 resize: "vertical",
//                 transition: "border-color 0.2s",
//                 outline: "none",
//                 boxSizing: "border-box", // Fix the overflow issue
//               }}
//               onFocus={(e) => (e.target.style.borderColor = "#6366f1")}
//               onBlur={(e) => (e.target.style.borderColor = "#d1d5db")}
//               disabled={loading}
//             />
//           </div>

//           {/* Prompt Suggestions */}
//           <div style={{ marginBottom: "20px" }}>
//             <p
//               style={{
//                 color: "#4b5563",
//                 fontSize: "14px",
//                 fontWeight: "500",
//                 marginBottom: "8px",
//               }}
//             >
//               Need inspiration? Try these:
//             </p>
//             <div
//               style={{
//                 display: "flex",
//                 flexWrap: "wrap",
//                 gap: "10px",
//               }}
//             >
//               {suggestions.map((suggestion, index) => (
//                 <button
//                   key={index}
//                   type="button"
//                   onClick={() => setPrompt(suggestion)}
//                   style={{
//                     background: "#f3f4f6",
//                     color: "#4b5563",
//                     border: "none",
//                     padding: "6px 12px",
//                     borderRadius: "6px",
//                     fontSize: "13px",
//                     cursor: "pointer",
//                     transition: "background 0.2s",
//                   }}
//                   onMouseOver={(e) => (e.target.style.background = "#e5e7eb")}
//                   onMouseOut={(e) => (e.target.style.background = "#f3f4f6")}
//                 >
//                   {suggestion}
//                 </button>
//               ))}
//             </div>
//           </div>

//           <div
//             style={{
//               display: "flex",
//               justifyContent: "flex-end",
//             }}
//           >
//             <button
//               type="submit"
//               disabled={loading}
//               style={{
//                 background: loading ? "#a5b4fc" : "#6366f1",
//                 color: "white",
//                 border: "none",
//                 padding: "10px 20px",
//                 borderRadius: "6px",
//                 cursor: loading ? "not-allowed" : "pointer",
//                 fontSize: "14px",
//                 fontWeight: "500",
//                 transition: "background 0.2s",
//                 display: "flex",
//                 alignItems: "center",
//                 gap: "8px",
//               }}
//               onMouseOver={(e) => {
//                 if (!loading) e.target.style.background = "#4f46e5";
//               }}
//               onMouseOut={(e) => {
//                 if (!loading) e.target.style.background = "#6366f1";
//               }}
//             >
//               {loading && <CircularProgress size={16} color="inherit" />}
//               {loading ? "Creating Task..." : "Create Task"}
//             </button>
//           </div>
//         </form>
//       </div>

//       {/* Snackbar for feedback */}
//       <Snackbar
//         open={snackbarOpen}
//         autoHideDuration={3000}
//         onClose={() => setSnackbarOpen(false)}
//         anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
//       >
//         <Alert
//           onClose={() => setSnackbarOpen(false)}
//           severity={snackbarSeverity}
//           sx={{ width: '100%' }}
//         >
//           {snackbarMessage}
//         </Alert>
//       </Snackbar>
//     </div>
//   );
// };

// export default AiAssistant;

import { useState } from "react";
import { Link } from "react-router-dom";
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

const AiAssistant = () => {
  const [prompt, setPrompt] = useState("");
  const [previousData, setPreviousData] = useState({});
  const [assistantMessage, setAssistantMessage] = useState("");
  const [taskPreview, setTaskPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");

  // Example prompt suggestions
  const suggestions = [
    "Create a high-priority task to design a logo for the marketing team",
    "Add a medium-priority task to write a report for John",
    "Create a low-priority task to schedule a meeting with Sarah"
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setSnackbarMessage("Please enter a prompt!");
      setSnackbarSeverity("error");
      setSnackbarOpen(true);
      return;
    }

    setLoading(true);
    // Send prompt to /ai-assistant endpoint
    fetch('http://localhost:8000/ai-assistant', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        previous_data: previousData
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to process prompt');
        }
        return response.json();
      })
      .then((data) => {
        setLoading(false);
        if (data.status === "incomplete") {
          setAssistantMessage(data.message);
          setPreviousData(data.previous_data);
          setTaskPreview(null);
          setPrompt(""); // Clear prompt for next input
        } else if (data.status === "complete") {
          setTaskPreview(data.task);
          setAssistantMessage("Task created successfully!");
          setPreviousData({});
          setPrompt("");
          setSnackbarMessage("Task created successfully!");
          setSnackbarSeverity("success");
          setSnackbarOpen(true);
        } else {
          throw new Error(data.message || "Unknown error");
        }
      })
      .catch((error) => {
        setLoading(false);
        setSnackbarMessage("Error: " + error.message);
        setSnackbarSeverity("error");
        setSnackbarOpen(true);
        console.error('Error processing prompt:', error);
      });
  };

  const handleConfirmTask = () => {
    setLoading(true);
    // Send task data to /tasks endpoint
    fetch('http://localhost:8000/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(previousData),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to create task');
        }
        return response.json();
      })
      .then((data) => {
        setLoading(false);
        setTaskPreview(data);
        setAssistantMessage("Task created successfully!");
        setPreviousData({});
        setSnackbarMessage("Task created successfully!");
        setSnackbarSeverity("success");
        setSnackbarOpen(true);
      })
      .catch((error) => {
        setLoading(false);
        setSnackbarMessage("Error creating task: " + error.message);
        setSnackbarSeverity("error");
        setSnackbarOpen(true);
        console.error('Error creating task:', error);
      });
  };

  const handleModifyTask = () => {
    setTaskPreview(null);
    setAssistantMessage("Please provide any modifications to the task data.");
  };

  return (
    <div
      style={{
        padding: "30px",
        maxWidth: "1200px",
        margin: "0 auto",
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
            AI Assistant
          </h2>
          <p
            style={{
              fontSize: "14px",
              color: "#6b7280",
              margin: 0,
            }}
          >
            Create tasks using natural language prompts
          </p>
        </div>
        <Link to="/" style={{ textDecoration: "none" }}>
          <Button
            variant="contained"
            startIcon={
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
                <path d="M19 12H5"></path>
                <path d="M12 19l-7-7 7-7"></path>
              </svg>
            }
          >
            Back to Dashboard
          </Button>
        </Link>
      </div>

      {/* Assistant Messages */}
      {assistantMessage && (
        <Box
          sx={{
            background: "#f0f9ff",
            borderRadius: "8px",
            padding: "16px",
            marginBottom: "20px",
            border: "1px solid #bae6fd",
          }}
        >
          <Typography variant="body1" color="textSecondary">
            {assistantMessage}
          </Typography>
        </Box>
      )}

      {/* Task Preview */}
      {previousData.stage === "confirm" && (
        <Box
          sx={{
            background: "#f9fafb",
            borderRadius: "8px",
            padding: "16px",
            marginBottom: "20px",
            border: "1px solid #e5e7eb",
          }}
        >
          <Typography variant="h6" gutterBottom>
            Task Preview
          </Typography>
          <pre
            style={{
              background: "#1f2937",
              color: "#f3f4f6",
              padding: "12px",
              borderRadius: "6px",
              overflowX: "auto",
            }}
          >
            {JSON.stringify(previousData, null, 2)}
          </pre>
          <Box sx={{ display: "flex", gap: "10px", marginTop: "10px" }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleConfirmTask}
              disabled={loading}
            >
              {loading ? <CircularProgress size={16} color="inherit" /> : "Confirm Task"}
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleModifyTask}
              disabled={loading}
            >
              Modify Task
            </Button>
          </Box>
        </Box>
      )}

      {/* Prompt Input Section */}
      <Box
        sx={{
          background: "white",
          borderRadius: "8px",
          padding: "20px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
          border: "1px solid #e5e7eb",
        }}
      >
        <form onSubmit={handleSubmit}>
          <Box sx={{ marginBottom: "20px" }}>
            <Typography
              variant="subtitle1"
              sx={{ marginBottom: "6px", color: "#4b5563", fontWeight: "500" }}
            >
              Enter Your Prompt
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., Create a high-priority task to design a logo for the marketing team"
              variant="outlined"
              disabled={loading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '& fieldset': { borderColor: '#d1d5db' },
                  '&:hover fieldset': { borderColor: '#6366f1' },
                  '&.Mui-focused fieldset': { borderColor: '#6366f1' },
                },
              }}
            />
          </Box>

          {/* Prompt Suggestions */}
          <Box sx={{ marginBottom: "20px" }}>
            <Typography
              variant="subtitle2"
              sx={{ color: "#4b5563", fontWeight: "500", marginBottom: "8px" }}
            >
              Need inspiration? Try these:
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
              {suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outlined"
                  onClick={() => setPrompt(suggestion)}
                  sx={{
                    background: "#f3f4f6",
                    color: "#4b5563",
                    border: "none",
                    textTransform: "none",
                    '&:hover': { background: "#e5e7eb" },
                  }}
                >
                  {suggestion}
                </Button>
              ))}
            </Box>
          </Box>

          <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              startIcon={loading && <CircularProgress size={16} color="inherit" />}
            >
              {loading ? "Processing..." : "Submit Prompt"}
            </Button>
          </Box>
        </form>
      </Box>

      {/* Snackbar for feedback */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default AiAssistant;