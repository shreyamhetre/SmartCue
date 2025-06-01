# import asyncio
# import logging
# import os
# import sys
# import traceback
# import json
# import httpx
# from dotenv import load_dotenv
# from fastmcp import FastMCP

# # Setup logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("ai_assistant_mcp.log"),
#         logging.StreamHandler(sys.stderr)
#     ]
# )
# logger = logging.getLogger("AIAssistantMCP")

# # Load environment variables
# load_dotenv()

# # Gemini API configuration
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# if not GEMINI_API_KEY:
#     logger.error("GEMINI_API_KEY not set")
#     sys.exit(1)

# GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# # Initialize MCP server
# app = FastMCP(server_name="AIAssistantMCP")

# # Task creation fields for validation
# TASK_FIELDS = {
#     "required": ["task_name", "description", "priority"],
#     "optional": ["assignee", "meeting_description", "assignee_for_meeting", "meeting_date", "meeting_time"]
# }

# async def call_gemini_api(prompt: str) -> dict:
#     """
#     Call the Gemini API to analyze the user prompt and return the response.
#     """
#     logger.info(f"Calling Gemini API with prompt: {prompt}")
#     headers = {
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "contents": [
#             {
#                 "parts": [
#                     {
#                         "text": prompt
#                     }
#                 ]
#             }
#         ]
#     }

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
#                 headers=headers,
#                 json=payload
#             )
#             if response.status_code != 200:
#                 error_text = response.text
#                 logger.error(f"Gemini API error: {response.status_code} - {error_text}")
#                 return {"status": "error", "message": f"Gemini API error: {error_text}"}
            
#             result = response.json()
#             if "candidates" not in result or not result["candidates"]:
#                 logger.error("No candidates in Gemini API response")
#                 return {"status": "error", "message": "No response from Gemini API"}
            
#             generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
#             logger.info(f"Gemini API response: {generated_text}")
#             return {"status": "success", "response": generated_text}
#     except Exception as e:
#         logger.error(f"Error calling Gemini API: {str(e)}")
#         return {"status": "error", "message": str(e)}

# @app.tool(name="analyze_prompt")
# async def analyze_prompt(user_prompt: str, previous_data: dict = None) -> dict:
#     """
#     Analyze the user prompt to identify missing fields, ask for assignee and meeting details,
#     or return task data for confirmation.
#     """
#     logger.info(f"Analyzing user prompt: {user_prompt}, Previous data: {previous_data}")

#     # Initialize partial data
#     partial_data = previous_data or {}
#     stage = partial_data.get("stage", "initial")

#     # Construct Gemini prompt based on stage
#     if stage == "initial":
#         gemini_prompt = (
#             f"The user wants to create a task with the following input: '{user_prompt}'.\n"
#             "The required fields are: task_name, description, priority (must be 'low', 'medium', or 'high').\n"
#             "Respond with strict JSON in the following format:\n"
#             "- If fields are missing, return: {{\"missing_fields\": [\"field1\", \"field2\"], \"partial_data\": {{}}}} with extracted fields in partial_data.\n"
#             "- If all required fields are present, return: {{\"partial_data\": {{\"task_name\": \"value\", \"description\": \"value\", \"priority\": \"value\"}}, \"stage\": \"ask_assignee\"}}.\n"
#             "Ensure priority is one of 'low', 'medium', 'high'. If not specified, default to 'medium'.\n"
#             "Interpret natural language for priority (e.g., 'little less' means 'low', 'urgent' means 'high', 'normal' means 'medium').\n"
#             "Return ONLY the JSON object."
#         )
#     elif stage == "ask_assignee":
#         gemini_prompt = (
#             f"The user previously provided: {json.dumps(previous_data)}.\n"
#             f"The user now provided: '{user_prompt}'.\n"
#             "Check if the user specified an assignee or declined to assign one.\n"
#             "Respond with strict JSON:\n"
#             "- If assignee is provided or declined, return: {{\"partial_data\": {{\"task_name\": \"value\", \"description\": \"value\", \"priority\": \"value\", \"assignee\": \"value\" or null}}, \"stage\": \"ask_meeting\"}}.\n"
#             "- If no clear response, return: {{\"missing_fields\": [\"assignee\"], \"partial_data\": {previous_data}}}.\n"
#             "Return ONLY the JSON object."
#         )
#     elif stage == "ask_meeting":
#         gemini_prompt = (
#             f"The user previously provided: {json.dumps(previous_data)}.\n"
#             f"The user now provided: '{user_prompt}'.\n"
#             "Check if the user wants to schedule a meeting (yes/no).\n"
#             "Respond with strict JSON:\n"
#             "- If 'no', return: {{\"partial_data\": {previous_data}, \"stage\": \"confirm\"}}.\n"
#             "- If 'yes', return: {{\"missing_fields\": [\"meeting_description\", \"assignee_for_meeting\", \"meeting_date\", \"meeting_time\"], \"partial_data\": {previous_data}, \"stage\": \"collect_meeting\"}}.\n"
#             "- If no clear response, return: {{\"missing_fields\": [\"meeting_decision\"], \"partial_data\": {previous_data}}}.\n"
#             "Return ONLY the JSON object."
#         )
#     elif stage == "collect_meeting":
#         gemini_prompt = (
#             f"The user previously provided: {json.dumps(previous_data)}.\n"
#             f"The user now provided: '{user_prompt}'.\n"
#             "Extract meeting details: meeting_description, assignee_for_meeting, meeting_date (YYYY-MM-DD), meeting_time (HH:MM).\n"
#             "Respond with strict JSON:\n"
#             "- If fields are missing, return: {{\"missing_fields\": [\"field1\", \"field2\"], \"partial_data\": {{updated fields}}}}.\n"
#             "- If all meeting fields are present, return: {{\"partial_data\": {{\"task_name\": \"value\", \"description\": \"value\", \"priority\": \"value\", \"assignee\": \"value\", \"meeting_description\": \"value\", \"assignee_for_meeting\": \"value\", \"meeting_date\": \"value\", \"meeting_time\": \"value\"}}, \"stage\": \"confirm\"}}.\n"
#             "Return ONLY the JSON object."
#         )
#     elif stage == "confirm":
#         gemini_prompt = (
#             f"The user previously provided: {json.dumps(previous_data)}.\n"
#             f"The user now provided: '{user_prompt}'.\n"
#             "Check if the user confirms the task or wants to modify fields.\n"
#             "Respond with strict JSON:\n"
#             "- If confirmed, return: {{\"task_data\": {previous_data}}}.\n"
#             "- If modifications provided, return: {{\"partial_data\": {{updated fields}}, \"stage\": \"confirm\"}}.\n"
#             "- If no clear response, return: {{\"missing_fields\": [\"confirmation\"], \"partial_data\": {previous_data}}}.\n"
#             "Return ONLY the JSON object."
#         )

#     # Call Gemini API
#     gemini_response = await call_gemini_api(gemini_prompt)
#     if gemini_response["status"] != "success":
#         return {"status": "error", "message": gemini_response["message"]}

#     response_text = gemini_response["response"]

#     # Parse Gemini's response
#     try:
#         # Extract JSON from response
#         json_start = response_text.find('{')
#         json_end = response_text.rfind('}') + 1
#         if json_start == -1 or json_end == 0:
#             logger.error(f"Failed to find JSON in Gemini response: {response_text}")
#             return {"status": "error", "message": "Invalid JSON format in Gemini response"}

#         json_text = response_text[json_start:json_end]
#         response_data = json.loads(json_text)

#         if "missing_fields" in response_data:
#             missing_fields = response_data["missing_fields"]
#             partial_data = response_data.get("partial_data", previous_data or {})
#             partial_data["stage"] = response_data.get("stage", stage)

#             # Construct polite prompts
#             prompts = []
#             if stage == "initial":
#                 for field in missing_fields:
#                     if field == "task_name":
#                         prompts.append("Can you provide the name of the task?")
#                     elif field == "description":
#                         prompts.append("Can you provide the description of the task?")
#                     elif field == "priority":
#                         prompts.append("What is the priority of the task (low, medium, or high)?")
#             elif stage == "ask_assignee":
#                 prompts.append("Would you like to assign this task to someone? If so, who?")
#             elif stage == "ask_meeting":
#                 prompts.append("Would you like to schedule a meeting for this task? Please respond with 'yes' or 'no'.")
#             elif stage == "collect_meeting":
#                 for field in missing_fields:
#                     if field == "meeting_description":
#                         prompts.append("What is the description of the meeting?")
#                     elif field == "assignee_for_meeting":
#                         prompts.append("Who should be assigned to the meeting?")
#                     elif field == "meeting_date":
#                         prompts.append("What is the date of the meeting (YYYY-MM-DD)?")
#                     elif field == "meeting_time":
#                         prompts.append("What is the time of the meeting (HH:MM)?")
#             elif stage == "confirm":
#                 prompts.append(f"Please review the task data: {json.dumps(partial_data, indent=2)}. Confirm by saying 'confirm' or provide modifications.")

#             prompt_message = " ".join(prompts)
#             return {
#                 "status": "incomplete",
#                 "message": prompt_message,
#                 "previous_data": partial_data
#             }
#         elif "task_data" in response_data:
#             task_data = response_data["task_data"]
#             missing_required = [field for field in TASK_FIELDS["required"] if field not in task_data or not task_data[field]]
#             if missing_required:
#                 return {
#                     "status": "error",
#                     "message": f"Gemintask_datai API returned incomplete data. Missing required fields: {missing_required}"
#                 }
#             return {"status": "complete", "task_data": task_data}
#         else:
#             logger.error(f"Unexpected Gemini response format: {response_text}")
#             return {"status": "error", "message": "Unexpected response format from Gemini API"}
#     except json.JSONDecodeError:
#         logger.error(f"Failed to parse Gemini response as JSON: {response_text}")
#         return {"status": "error", "message": "Invalid response format from Gemini API"}

# async def start_server():
#     logger.info("Starting AI Assistant MCP server on TCP port 9003...")
#     try:
#         async def handle_connection(reader, writer):
#             try:
#                 await app.run(connection=(reader, writer))
#             except Exception as e:
#                 logger.error(f"Error handling connection: {str(e)}")
#                 logger.error(traceback.format_exc())
#             finally:
#                 try:
#                     writer.close()
#                     await writer.wait_closed()
#                 except Exception as e:
#                     logger.error(f"Error closing writer: {str(e)}")
            
#         server = await asyncio.start_server(
#             handle_connection,
#             '127.0.0.1',
#             9003
#         )
#         logger.info("AI Assistant MCP TCP server started")
#         return server
#     except Exception as e:
#         logger.error(f"AI Assistant MCP server error: {str(e)}")
#         return None

# if __name__ == "__main__":
#     try:
#         asyncio.run(start_server())
#     except KeyboardInterrupt:
#         logger.info("AI Assistant MCP server stopped by user")
#         sys.exit(0)
#     except Exception as e:
#         logger.error(f"AI Assistant MCP server critical error: {str(e)}")
#         sys.exit(1)


import asyncio
import logging
import os
import sys
import traceback
import json
import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_assistant_mcp.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("AIAssistantMCP")

# Load environment variables
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not set")
    sys.exit(1)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Initialize MCP server
app = FastMCP(server_name="AIAssistantMCP")

# Task creation fields for validation
TASK_FIELDS = {
    "required": ["task_name", "description", "priority"],
    "optional": ["assignee", "meeting_description", "assignee_for_meeting", "meeting_date", "meeting_time"]
}

async def call_gemini_api(prompt: str) -> dict:
    """
    Call the Gemini API to analyze the user prompt and return the response.
    """
    logger.info(f"Calling Gemini API with prompt: {prompt}")
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=payload
            )
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Gemini API error: {response.status_code} - {error_text}")
                return {"status": "error", "message": f"Gemini API error: {error_text}"}
            
            result = response.json()
            if "candidates" not in result or not result["candidates"]:
                logger.error("No candidates in Gemini API response")
                return {"status": "error", "message": "No response from Gemini API"}
            
            generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
            logger.info(f"Gemini API response: {generated_text}")
            return {"status": "success", "response": generated_text}
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.tool(name="analyze_prompt")
async def analyze_prompt(user_prompt: str, previous_data: dict = None) -> dict:
    """
    Analyze the user prompt to identify missing fields, ask for assignee and meeting details,
    or return task data for confirmation.
    """
    logger.info(f"Analyzing user prompt: {user_prompt}, Previous data: {previous_data}")

    # Initialize partial data
    partial_data = previous_data or {}
    stage = partial_data.get("stage", "initial")

    # Construct Gemini prompt based on stage
    if stage == "initial":
        gemini_prompt = (
            f"The user wants to create a task with the following input: '{user_prompt}'.\n"
            "The required fields are: task_name, description, priority (must be 'low', 'medium', or 'high').\n"
            "Optional fields: assignee, meeting_description, assignee_for_meeting, meeting_date (YYYY-MM-DD), meeting_time (HH:MM).\n"
            "Respond with strict JSON (no Markdown or code blocks) in the following format:\n"
            "- If fields are missing, return: {{\"missing_fields\": [\"field1\", \"field2\"], \"partial_data\": {{}}}} with extracted fields in partial_data.\n"
            "- If all required fields are present, return: {{\"partial_data\": {{\"task_name\": \"value\", \"description\": \"value\", \"priority\": \"value\", ...}}, \"stage\": \"ask_assignee\"}}.\n"
            "Ensure priority is one of 'low', 'medium', 'high'. If not specified, default to 'medium'.\n"
            "Interpret natural language for priority (e.g., 'little less' means 'low', 'urgent' means 'high', 'normal' means 'medium').\n"
            "Return ONLY the JSON object, no additional text or formatting."
        )
    elif stage == "ask_assignee":
        gemini_prompt = (
            f"The user previously provided: {json.dumps(previous_data)}.\n"
            f"The user now provided: '{user_prompt}'.\n"
            "Check if the user specified an assignee or declined to assign one.\n"
            "Respond with strict JSON (no Markdown or code blocks):\n"
            "- If assignee is provided or declined, return: {{\"partial_data\": {{\"task_name\": \"value\", \"description\": \"value\", \"priority\": \"value\", \"assignee\": \"value\" or null, ...}}, \"stage\": \"ask_meeting\"}}.\n"
            "- If no clear response, return: {{\"missing_fields\": [\"assignee\"], \"partial_data\": {previous_data}}}.\n"
            "Return ONLY the JSON object, no additional text or formatting."
        )
    elif stage == "ask_meeting":
        gemini_prompt = (
            f"The user previously provided: {json.dumps(previous_data)}.\n"
            f"The user now provided: '{user_prompt}'.\n"
            "Check if the user wants to schedule a meeting (yes/no).\n"
            "Respond with strict JSON (no Markdown or code blocks):\n"
            "- If 'no', return: {{\"partial_data\": {previous_data}, \"stage\": \"confirm\"}}.\n"
            "- If 'yes', return: {{\"missing_fields\": [\"meeting_description\", \"assignee_for_meeting\", \"meeting_date\", \"meeting_time\"], \"partial_data\": {previous_data}, \"stage\": \"collect_meeting\"}}.\n"
            "- If no clear response, return: {{\"missing_fields\": [\"meeting_decision\"], \"partial_data\": {previous_data}}}.\n"
            "Return ONLY the JSON object, no additional text or formatting."
        )
    elif stage == "collect_meeting":
        gemini_prompt = (
            f"The user previously provided: {json.dumps(previous_data)}.\n"
            f"The user now provided: '{user_prompt}'.\n"
            "Extract meeting details: meeting_description, assignee_for_meeting, meeting_date (YYYY-MM-DD), meeting_time (HH:MM).\n"
            "Respond with strict JSON (no Markdown or code blocks):\n"
            "- If fields are missing, return: {{\"missing_fields\": [\"field1\", \"field2\"], \"partial_data\": {{updated fields}}}}.\n"
            "- If all meeting fields are present, return: {{\"partial_data\": {{\"task_name\": \"value\", \"description\": \"value\", \"priority\": \"value\", \"assignee\": \"value\", \"meeting_description\": \"value\", \"assignee_for_meeting\": \"value\", \"meeting_date\": \"value\", \"meeting_time\": \"value\", ...}}, \"stage\": \"confirm\"}}.\n"
            "Return ONLY the JSON object, no additional text or formatting."
        )
    elif stage == "confirm":
        gemini_prompt = (
            f"The user previously provided: {json.dumps(previous_data)}.\n"
            f"The user now provided: '{user_prompt}'.\n"
            "Check if the user confirms the task or wants to modify fields.\n"
            "Respond with strict JSON (no Markdown or code blocks):\n"
            "- If confirmed (e.g., 'confirm'), return: {{\"task_data\": {previous_data}}}.\n"
            "- If modifications provided, return: {{\"partial_data\": {{updated fields}}, \"stage\": \"confirm\"}}.\n"
            "- If no clear response, return: {{\"missing_fields\": [\"confirmation\"], \"partial_data\": {previous_data}}}.\n"
            "Return ONLY the JSON object, no additional text or formatting."
        )

    # Call Gemini API
    gemini_response = await call_gemini_api(gemini_prompt)
    if gemini_response["status"] != "success":
        return {"status": "error", "message": gemini_response["message"]}

    response_text = gemini_response["response"]

    # Parse Gemini's response
    try:
        # Remove potential Markdown code blocks
        cleaned_response = response_text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()

        # Parse JSON
        response_data = json.loads(cleaned_response)

        if "missing_fields" in response_data:
            missing_fields = response_data["missing_fields"]
            partial_data = response_data.get("partial_data", previous_data or {})
            partial_data["stage"] = response_data.get("stage", stage)

            # Construct polite prompts
            prompts = []
            if stage == "initial":
                for field in missing_fields:
                    if field == "task_name":
                        prompts.append("Can you provide the name of the task?")
                    elif field == "description":
                        prompts.append("Can you provide the description of the task?")
                    elif field == "priority":
                        prompts.append("What is the priority of the task (low, medium, or high)?")
            elif stage == "ask_assignee":
                prompts.append("Would you like to assign this task to someone? If so, who?")
            elif stage == "ask_meeting":
                prompts.append("Would you like to schedule a meeting for this task? Please respond with 'yes' or 'no'.")
            elif stage == "collect_meeting":
                for field in missing_fields:
                    if field == "meeting_description":
                        prompts.append("What is the description of the meeting?")
                    elif field == "assignee_for_meeting":
                        prompts.append("Who should be assigned to the meeting?")
                    elif field == "meeting_date":
                        prompts.append("What is the date of the meeting (YYYY-MM-DD)?")
                    elif field == "meeting_time":
                        prompts.append("What is the time of the meeting (HH:MM)?")
            elif stage == "confirm":
                prompts.append(f"Please review the task data: {json.dumps(partial_data, indent=2)}. Confirm by saying 'confirm' or provide modifications.")

            prompt_message = " ".join(prompts)
            return {
                "status": "incomplete",
                "message": prompt_message,
                "previous_data": partial_data
            }
        elif "partial_data" in response_data:
            partial_data = response_data["partial_data"]
            partial_data["stage"] = response_data.get("stage", stage)
            prompt_message = ""
            if response_data["stage"] == "ask_assignee":
                prompt_message = "Would you like to assign this task to someone? If so, who?"
            elif response_data["stage"] == "ask_meeting":
                prompt_message = "Would you like to schedule a meeting for this task? Please respond with 'yes' or 'no'."
            elif response_data["stage"] == "confirm":
                prompt_message = f"Please review the task data: {json.dumps(partial_data, indent=2)}. Confirm by saying 'confirm' or provide modifications."
            return {
                "status": "incomplete",
                "message": prompt_message,
                "previous_data": partial_data
            }
        elif "task_data" in response_data:
            task_data = response_data["task_data"]
            missing_required = [field for field in TASK_FIELDS["required"] if field not in task_data or not task_data[field]]
            if missing_required:
                return {
                    "status": "error",
                    "message": f"Gemini API returned incomplete data. Missing required fields: {missing_required}"
                }
            return {"status": "complete", "task_data": task_data}
        else:
            logger.error(f"Unexpected Gemini response format: {response_text}")
            return {"status": "error", "message": "Unexpected response format from Gemini API"}
    except json.JSONDecodeError:
        logger.error(f"Failed to parse Gemini response as JSON: {cleaned_response}")
        return {"status": "error", "message": "Invalid response format from Gemini API"}

async def start_server():
    logger.info("Starting AI Assistant MCP server on TCP port 9003...")
    try:
        async def handle_connection(reader, writer):
            try:
                await app.run(connection=(reader, writer))
            except Exception as e:
                logger.error(f"Error handling connection: {str(e)}")
                logger.error(traceback.format_exc())
            finally:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception as e:
                    logger.error(f"Error closing writer: {str(e)}")
            
        server = await asyncio.start_server(
            handle_connection,
            '127.0.0.1',
            9003
        )
        logger.info("AI Assistant MCP TCP server started")
        return server
    except Exception as e:
        logger.error(f"AI Assistant MCP server error: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("AI Assistant MCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"AI Assistant MCP server critical error: {str(e)}")
        sys.exit(1)