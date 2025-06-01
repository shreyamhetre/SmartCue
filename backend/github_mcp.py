import asyncio
import logging
import os
import sys
import traceback
import json
from dotenv import load_dotenv
from github import Github
from github.GithubException import GithubException
from fastmcp import FastMCP
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("github_mcp.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("GitHubMCP")

# Load environment variables
load_dotenv()

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    logger.error("GITHUB_TOKEN not set")
    sys.exit(1)
REPO_NAME = os.getenv("REPO_NAME", "shreyamhetre/SmartCue")

# Initialize MCP server
app = FastMCP(server_name="GitHubMCP")

# Create a global thread pool executor for blocking operations
thread_pool = ThreadPoolExecutor(max_workers=5)

# GitHub client initialization
def init_github():
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        logger.info(f"Connected to GitHub repo: {REPO_NAME}")
        return repo
    except Exception as e:
        logger.error(f"Failed to connect to GitHub: {str(e)}")
        return None

# Global repo object
repo = init_github()

# Helper function to create GitHub issue in a thread pool
def _create_github_issue(title, body, labels, assignee=None):
    """Execute GitHub API call in a separate thread"""
    try:
        global repo
        if not repo:
            repo = init_github()
            if not repo:
                raise Exception("Could not connect to GitHub repository")
                
        logger.debug(f"Creating GitHub issue: {title}")
        
        # Create the issue
        issue = repo.create_issue(
            title=title,
            body=body or "",
            labels=labels
        )
        
        # Assign the issue if an assignee is provided
        if assignee:
            try:
                issue.add_to_assignees(assignee)
                logger.info(f"Assigned issue to: {assignee}")
            except GithubException as ge:
                if ge.status == 404:
                    raise Exception(f"GitHub user '{assignee}' not found or doesn't have access to this repository")
                elif ge.status == 403:
                    raise Exception(f"Not allowed to assign issues to '{assignee}'. Make sure they are a collaborator.")
                else:
                    raise
            
        logger.info(f"GitHub issue created: {issue.html_url}")
        return {
            "issue_id": issue.id,
            "issue_number": issue.number,  # Add issue number for state updates
            "issue_url": issue.html_url,
            "title": issue.title,
            "assignee": assignee
        }
    except GithubException as ge:
        logger.error(f"GitHub API error: {ge.status} - {ge.data}")
        error_msg = f"GitHub API error: {ge.status} - {ge.data.get('message', '')}"
        raise Exception(error_msg)
    except Exception as e:
        logger.error(f"Failed to create GitHub issue: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Helper function to get GitHub issues in a thread pool
def _get_github_issues(state):
    """Execute GitHub API call in a separate thread"""
    try:
        global repo
        if not repo:
            repo = init_github()
            if not repo:
                raise Exception("Could not connect to GitHub repository")
                
        logger.debug(f"Retrieving GitHub issues with state: {state}")
        issues = list(repo.get_issues(state=state))
        
        issue_list = [
            {
                "issue_id": issue.id,
                "title": issue.title,
                "url": issue.html_url,
                "state": issue.state,
                "labels": [label.name for label in issue.labels]
            }
            for issue in issues
        ]
        
        logger.info(f"Retrieved {len(issue_list)} issues")
        return issue_list
    except GithubException as ge:
        logger.error(f"GitHub API error: {ge.status} - {ge.data}")
        error_msg = f"GitHub API error: {ge.status} - {ge.data.get('message', '')}"
        raise Exception(error_msg)
    except Exception as e:
        logger.error(f"Failed to retrieve GitHub issues: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Helper function to update GitHub issue state in a thread pool
def _update_issue_state(issue_number, state, labels):
    """Execute GitHub API call to update issue state in a separate thread"""
    try:
        global repo
        if not repo:
            repo = init_github()
            if not repo:
                raise Exception("Could not connect to GitHub repository")
                
        logger.debug(f"Updating GitHub issue #{issue_number} to state: {state}")
        issue = repo.get_issue(number=issue_number)  # Use issue number
        issue.edit(state=state, labels=labels)
        logger.info(f"GitHub issue #{issue_number} updated to state: {state}")
        return {"status": "success"}
    except GithubException as ge:
        logger.error(f"GitHub API error: {ge.status} - {ge.data}")
        error_msg = f"GitHub API error: {ge.status} - {ge.data.get('message', '')}"
        raise Exception(error_msg)
    except Exception as e:
        logger.error(f"Failed to update GitHub issue state: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Tool: create_github_issue - Fixed to use thread pool without event loop conflicts
@app.tool(name="create_github_issue")
async def create_github_issue(title: str, body: str, labels: list, assignee: str | None = None) -> dict:
    logger.info(f"Creating GitHub issue: {title}")
    try:
        # Execute GitHub API call in a thread pool
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            thread_pool, 
            lambda: _create_github_issue(title, body, labels, assignee)
        )
        logger.debug(f"Sending response: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to create GitHub issue: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Tool: get_github_issues - Fixed to use thread pool without event loop conflicts
@app.tool(name="get_github_issues")
async def get_github_issues(state: str = "open") -> list:
    logger.info(f"Retrieving GitHub issues with state: {state}")
    try:
        # Execute GitHub API call in a thread pool
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(thread_pool, lambda: _get_github_issues(state))
        logger.debug(f"Sending response: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to retrieve GitHub issues: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Tool: update_issue_state - Added to handle issue state updates
@app.tool(name="update_issue_state")
async def update_issue_state(issue_number: int, state: str, labels: list) -> dict:
    logger.info(f"Updating GitHub issue #{issue_number} to state: {state}")
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            thread_pool, 
            lambda: _update_issue_state(issue_number, state, labels)
        )
        logger.debug(f"Sending response: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to update GitHub issue state: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Function to start the server (will be called from main.py)
async def start_server():
    logger.info("Starting GitHub MCP server on TCP port 9000...")
    try:
        if not repo:
            logger.error("Cannot start GitHub MCP server: GitHub connection failed")
            return None
        
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
            9000
        )
        logger.info("GitHub MCP TCP server started")
        return server
    except Exception as e:
        logger.error(f"GitHub MCP server error: {str(e)}")
        logger.error(traceback.format_exc())
        return None

# Clean shutdown for thread pool
def cleanup():
    thread_pool.shutdown(wait=True)
    logger.info("Thread pool shut down")

# Run MCP server over TCP if executed directly
if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("GitHub MCP server stopped by user")
        cleanup()
        sys.exit(0)
    except Exception as e:
        logger.error(f"GitHub MCP server critical error: {str(e)}")
        logger.error(traceback.format_exc())
        cleanup()
        sys.exit(1)