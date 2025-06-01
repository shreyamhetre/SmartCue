# import os
# import sys
# import logging
# import asyncio
# import json
# from typing import Optional, List, Dict, Any
# from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from datetime import datetime

# from fastapi.middleware.cors import CORSMiddleware
# from . import github_mcp, postgres_mcp, calendar_mcp  # Add calendar_mcp import

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# load_dotenv()

# app = FastAPI(title="Task Automation API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# github_server = None
# postgres_server = None
# calendar_server = None  # Add calendar server

# class TaskCreate(BaseModel):
#     task_name: str
#     description: Optional[str] = None
#     priority: str
#     assignee: Optional[str] = None
#     meeting_description: Optional[str] = None  # New meeting fields
#     assignee_for_meeting: Optional[str] = None
#     meeting_date: Optional[str] = None  # Format: "YYYY-MM-DD"
#     meeting_time: Optional[str] = None  # Format: "HH:MM"

# class TaskResponse(BaseModel):
#     task_id: int
#     task_name: str
#     github_issue_url: str
#     status: str = "success"
#     assignee: Optional[str] = None
#     meeting_description: Optional[str] = None  # Include meeting fields in response
#     assignee_for_meeting: Optional[str] = None
#     meeting_datetime: Optional[str] = None

# class TaskList(BaseModel):
#     tasks: List[Dict[str, Any]]

# @app.on_event("startup")
# async def startup_event():
#     global github_server, postgres_server, calendar_server
#     logger.info("Starting MCP servers...")
    
#     # Start GitHub MCP server
#     github_server = await github_mcp.start_server()
#     if not github_server:
#         logger.error("Failed to start GitHub MCP server")
#         return
        
#     # Start Postgres MCP server
#     postgres_server = await postgres_mcp.start_server()
#     if not postgres_server:
#         logger.error("Failed to start Postgres MCP server")
#         return
        
#     # Start Calendar MCP server
#     calendar_server = await calendar_mcp.start_server()
#     if not calendar_server:
#         logger.error("Failed to start Calendar MCP server")
#         return
        
#     logger.info("All MCP servers started successfully")

# @app.on_event("shutdown")
# async def shutdown_event():
#     if github_server:
#         github_server.close()
#         await github_server.wait_closed()
#     if postgres_server:
#         postgres_server.close()
#         await postgres_server.wait_closed()
#     if calendar_server:
#         calendar_server.close()
#         await calendar_server.wait_closed()
#     logger.info("MCP servers shut down")

# @app.post("/tasks", response_model=TaskResponse)
# async def create_task(task: TaskCreate):
#     try:
#         # Validate priority
#         if task.priority not in ["low", "medium", "high"]:
#             raise HTTPException(
#                 status_code=400, 
#                 detail="Invalid priority. Must be 'low', 'medium', or 'high'."
#             )
        
#         # Create GitHub issue with priority label
#         labels = [f"priority:{task.priority}"]
#         issue = await github_mcp.create_github_issue(
#             task.task_name,
#             task.description or "",
#             labels,
#             assignee=task.assignee
#         )
        
#         # Combine meeting_date and meeting_time into meeting_datetime
#         meeting_datetime = None
#         if task.meeting_date and task.meeting_time:
#             try:
#                 meeting_datetime = datetime.strptime(
#                     f"{task.meeting_date} {task.meeting_time}",
#                     "%Y-%m-%d %H:%M"
#                 ).isoformat()
#             except ValueError:
#                 raise HTTPException(
#                     status_code=400,
#                     detail="Invalid meeting_date or meeting_time format. Use YYYY-MM-DD and HH:MM."
#                 )

#         # Store in PostgreSQL with default status "open" and meeting details
#         db_task = await postgres_mcp.insert_task(
#             task_name=task.task_name,
#             description=task.description or "",
#             github_issue_id=issue["issue_id"],
#             github_issue_url=issue["issue_url"],
#             status="open",
#             priority=task.priority,
#             assignee=task.assignee,
#             meeting_description=task.meeting_description,
#             assignee_for_meeting=task.assignee_for_meeting,
#             meeting_datetime=meeting_datetime
#         )
        
#         # If meeting fields are provided, update meeting details in Calendar MCP
#         if all([task.meeting_description, task.assignee_for_meeting, meeting_datetime]):
#             await calendar_mcp.update_meeting(
#                 task_id=db_task["task_id"],
#                 meeting_description=task.meeting_description,
#                 assignee_for_meeting=task.assignee_for_meeting,
#                 meeting_datetime=meeting_datetime
#             )

#         return {
#             "task_id": db_task["task_id"],
#             "task_name": task.task_name,
#             "github_issue_url": issue["issue_url"],
#             "status": "success",
#             "assignee": task.assignee,
#             "meeting_description": task.meeting_description,
#             "assignee_for_meeting": task.assignee_for_meeting,
#             "meeting_datetime": meeting_datetime
#         }
        
#     except Exception as e:
#         logger.error(f"Error creating task: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/tasks", response_model=TaskList)
# async def get_tasks(
#     status: Optional[str] = None,
#     priority: Optional[str] = None,
#     assignee: Optional[str] = None
# ):
#     try:
#         if status and status not in ["open", "notplanned", "completed"]:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Invalid status. Must be 'open', 'notplanned', or 'completed'."
#             )
#         if priority and priority not in ["low", "medium", "high"]:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Invalid priority. Must be 'low', 'medium', or 'high'."
#             )
            
#         tasks = await postgres_mcp.get_tasks(status=status, priority=priority, assignee=assignee)
#         return {"tasks": tasks}
        
#     except Exception as e:
#         logger.error(f"Error retrieving tasks: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/webhooks")
# async def handle_webhook(request: Request):
#     try:
#         payload = await request.json()
#         action = payload.get("action", "")
#         issue = payload.get("issue", {})
#         github_issue_id = issue.get("id")
#         state = issue.get("state", "")
#         labels = [label["name"].lower() for label in issue.get("labels", [])]
        
#         logger.info(f"Webhook received - Action: {action}, State: {state}, Labels: {labels}, Issue ID: {github_issue_id}")
        
#         if action in ["opened", "closed", "reopened", "labeled", "unlabeled"]:
#             if state == "closed":
#                 if "completed" in labels:
#                     new_status = "completed"
#                 elif "notplanned" in labels:
#                     new_status = "notplanned"
#                 else:
#                     new_status = "completed"
#             else:
#                 if "notplanned" in labels:
#                     new_status = "notplanned"
#                 else:
#                     new_status = "open"
                    
#             logger.info(f"Updating task status to: {new_status} for issue ID: {github_issue_id}")
#             result = await postgres_mcp.update_task_status(github_issue_id, new_status)
#             if result["status"] == "error":
#                 logger.error(f"Failed to update task status: {result['message']}")
#                 raise HTTPException(status_code=404, detail=result["message"])

#             logger.info(f"Task updated successfully for GitHub issue ID: {github_issue_id} to status: {new_status}")
#             return {"status": "success"}
            
#         logger.info(f"Ignoring action: {action}")
#         return {"status": "ignored"}

#     except json.JSONDecodeError:
#         logger.error("Invalid JSON payload")
#         raise HTTPException(status_code=400, detail="Invalid JSON payload")
#     except KeyError as e:
#         logger.error(f"Missing required field in webhook payload: {str(e)}")
#         raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/meetings")
# async def get_meetings(start_date: Optional[str] = None, end_date: Optional[str] = None):
#     try:
#         meetings = await calendar_mcp.get_meetings(start_date=start_date, end_date=end_date)
#         return {"meetings": meetings}
#     except Exception as e:
#         logger.error(f"Error retrieving meetings: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))    
    
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

import os
import sys
import logging
import asyncio
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware
from . import github_mcp, postgres_mcp, calendar_mcp, ai_assistant_mcp

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Task Automation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

github_server = None
postgres_server = None
calendar_server = None
ai_assistant_server = None

class TaskCreate(BaseModel):
    task_name: str
    description: Optional[str] = None
    priority: str
    assignee: Optional[str] = None
    meeting_description: Optional[str] = None
    assignee_for_meeting: Optional[str] = None
    meeting_date: Optional[str] = None
    meeting_time: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: int
    task_name: str
    github_issue_url: str
    status: str = "success"
    assignee: Optional[str] = None
    meeting_description: Optional[str] = None
    assignee_for_meeting: Optional[str] = None
    meeting_datetime: Optional[str] = None

class TaskList(BaseModel):
    tasks: List[Dict[str, Any]]

class AIAssistantRequest(BaseModel):
    prompt: str
    previous_data: Optional[dict] = None

class AIAssistantResponse(BaseModel):
    status: str
    message: Optional[str] = None
    previous_data: Optional[dict] = None
    task: Optional[TaskResponse] = None

@app.on_event("startup")
async def startup_event():
    global github_server, postgres_server, calendar_server, ai_assistant_server
    logger.info("Starting MCP servers...")
    
    github_server = await github_mcp.start_server()
    if not github_server:
        logger.error("Failed to start GitHub MCP server")
        return
        
    postgres_server = await postgres_mcp.start_server()
    if not postgres_server:
        logger.error("Failed to start Postgres MCP server")
        return
        
    calendar_server = await calendar_mcp.start_server()
    if not calendar_server:
        logger.error("Failed to start Calendar MCP server")
        return
        
    ai_assistant_server = await ai_assistant_mcp.start_server()
    if not ai_assistant_server:
        logger.error("Failed to start AI Assistant MCP server")
        return
        
    logger.info("All MCP servers started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    if github_server:
        github_server.close()
        await github_server.wait_closed()
    if postgres_server:
        postgres_server.close()
        await postgres_server.wait_closed()
    if calendar_server:
        calendar_server.close()
        await calendar_server.wait_closed()
    if ai_assistant_server:
        ai_assistant_server.close()
        await ai_assistant_server.wait_closed()
    logger.info("MCP servers shut down")

@app.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    try:
        if task.priority not in ["low", "medium", "high"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid priority. Must be 'low', 'medium', or 'high'."
            )
        
        labels = [f"priority:{task.priority}"]
        issue = await github_mcp.create_github_issue(
            task.task_name,
            task.description or "",
            labels,
            assignee=task.assignee
        )
        
        meeting_datetime = None
        if task.meeting_date and task.meeting_time:
            try:
                meeting_datetime = datetime.strptime(
                    f"{task.meeting_date} {task.meeting_time}",
                    "%Y-%m-%d %H:%M"
                ).isoformat()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid meeting_date or meeting_time format. Use YYYY-MM-DD and HH:MM."
                )

        db_task = await postgres_mcp.insert_task(
            task_name=task.task_name,
            description=task.description or "",
            github_issue_id=issue["issue_id"],
            github_issue_url=issue["issue_url"],
            status="open",
            priority=task.priority,
            assignee=task.assignee,
            meeting_description=task.meeting_description,
            assignee_for_meeting=task.assignee_for_meeting,
            meeting_datetime=meeting_datetime
        )
        
        if all([task.meeting_description, task.assignee_for_meeting, meeting_datetime]):
            await calendar_mcp.update_meeting(
                task_id=db_task["task_id"],
                meeting_description=task.meeting_description,
                assignee_for_meeting=task.assignee_for_meeting,
                meeting_datetime=meeting_datetime
            )

        return {
            "task_id": db_task["task_id"],
            "task_name": task.task_name,
            "github_issue_url": issue["issue_url"],
            "status": "success",
            "assignee": task.assignee,
            "meeting_description": task.meeting_description,
            "assignee_for_meeting": task.assignee_for_meeting,
            "meeting_datetime": meeting_datetime
        }
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks", response_model=TaskList)
async def get_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None
):
    try:
        if status and status not in ["open", "notplanned", "completed"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid status. Must be 'open', 'notplanned', or 'completed'."
            )
        if priority and priority not in ["low", "medium", "high"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid priority. Must be 'low', 'medium', or 'high'."
            )
            
        tasks = await postgres_mcp.get_tasks(status=status, priority=priority, assignee=assignee)
        return {"tasks": tasks}
        
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()
        action = payload.get("action", "")
        issue = payload.get("issue", {})
        github_issue_id = issue.get("id")
        state = issue.get("state", "")
        labels = [label["name"].lower() for label in issue.get("labels", [])]
        
        logger.info(f"Webhook received - Action: {action}, State: {state}, Labels: {labels}, Issue ID: {github_issue_id}")
        
        if action in ["opened", "closed", "reopened", "labeled", "unlabeled"]:
            if state == "closed":
                if "completed" in labels:
                    new_status = "completed"
                elif "notplanned" in labels:
                    new_status = "notplanned"
                else:
                    new_status = "completed"
            else:
                if "notplanned" in labels:
                    new_status = "notplanned"
                else:
                    new_status = "open"
                    
            logger.info(f"Updating task status to: {new_status} for issue ID: {github_issue_id}")
            result = await postgres_mcp.update_task_status(github_issue_id, new_status)
            if result["status"] == "error":
                logger.error(f"Failed to update task status: {result['message']}")
                raise HTTPException(status_code=404, detail=result["message"])

            logger.info(f"Task updated successfully for GitHub issue ID: {github_issue_id} to status: {new_status}")
            return {"status": "success"}
            
        logger.info(f"Ignoring action: {action}")
        return {"status": "ignored"}

    except json.JSONDecodeError:
        logger.error("Invalid JSON payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except KeyError as e:
        logger.error(f"Missing required field in webhook payload: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meetings")
async def get_meetings(start_date: Optional[str] = None, end_date: Optional[str] = None):
    try:
        meetings = await calendar_mcp.get_meetings(start_date=start_date, end_date=end_date)
        return {"meetings": meetings}
    except Exception as e:
        logger.error(f"Error retrieving meetings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai-assistant", response_model=AIAssistantResponse)
async def ai_assistant(request: AIAssistantRequest):
    """
    AI Assistant endpoint to process user prompts and create tasks.
    If fields are missing, prompts the user for them. If complete, creates the task.
    """
    try:
        # Analyze the user prompt using the AI Assistant MCP
        analysis = await ai_assistant_mcp.analyze_prompt(
            request.prompt,
            previous_data=request.previous_data
        )
        logger.info(f"AI Assistant analysis: {analysis}")

        if analysis["status"] == "error":
            raise HTTPException(status_code=500, detail=analysis["message"])

        if analysis["status"] == "incomplete":
            # Return polite prompt for missing fields with previous_data
            return {
                "status": "incomplete",
                "message": analysis["message"],
                "previous_data": analysis["previous_data"],
                "task": None
            }

        # Create task if all required fields are present and confirmed
        task_data = analysis["task_data"]
        
        if task_data["priority"] not in ["low", "medium", "high"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid priority. Must be 'low', 'medium', or 'high'."
            )

        labels = [f"priority:{task_data['priority']}"]
        issue = await github_mcp.create_github_issue(
            task_data["task_name"],
            task_data.get("description", ""),
            labels,
            assignee=task_data.get("assignee")
        )

        meeting_datetime = None
        if "meeting_date" in task_data and "meeting_time" in task_data:
            try:
                meeting_datetime = datetime.strptime(
                    f"{task_data['meeting_date']} {task_data['meeting_time']}",
                    "%Y-%m-%d %H:%M"
                ).isoformat()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid meeting_date or meeting_time format. Use YYYY-MM-DD and HH:MM."
                )

        db_task = await postgres_mcp.insert_task(
            task_name=task_data["task_name"],
            description=task_data.get("description", ""),
            github_issue_id=issue["issue_id"],
            github_issue_url=issue["issue_url"],
            status="open",
            priority=task_data["priority"],
            assignee=task_data.get("assignee"),
            meeting_description=task_data.get("meeting_description"),
            assignee_for_meeting=task_data.get("assignee_for_meeting"),
            meeting_datetime=meeting_datetime
        )

        if all([
            task_data.get("meeting_description"),
            task_data.get("assignee_for_meeting"),
            meeting_datetime
        ]):
            await calendar_mcp.update_meeting(
                task_id=db_task["task_id"],
                meeting_description=task_data["meeting_description"],
                assignee_for_meeting=task_data["assignee_for_meeting"],
                meeting_datetime=meeting_datetime
            )

        return {
            "status": "complete",
            "task": {
                "task_id": db_task["task_id"],
                "task_name": task_data["task_name"],
                "github_issue_url": issue["issue_url"],
                "status": "success",
                "assignee": task_data.get("assignee"),
                "meeting_description": task_data.get("meeting_description"),
                "assignee_for_meeting": task_data.get("assignee_for_meeting"),
                "meeting_datetime": meeting_datetime
            },
            "previous_data": None,
            "message": None
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in AI Assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)