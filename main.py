import os
import httpx
import google.generativeai as genai
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Fetch secrets from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)
# Initialize the generative model
model = genai.GenerativeModel('gemini-1.5-flash') # Use a fast and capable model

# --- FastAPI Application ---
app = FastAPI()

# --- Helper Functions ---
async def get_pull_request_diff(diff_url: str) -> str:
    """Fetches the diff of a pull request from its diff URL."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff" # Request the diff format
    }
    # FIX: Initialize the client to follow redirects from GitHub
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(diff_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad responses (4xx or 5xx)
        return response.text

async def post_review_comment(comments_url: str, comment_body: str):
    """Posts a comment on the pull request."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment_body}
    async with httpx.AsyncClient() as client:
        response = await client.post(comments_url, headers=headers, json=data)
        response.raise_for_status()

def generate_review_prompt(diff: str) -> str:
    """Creates the prompt for the Gemini API."""
    # This prompt is engineered to give structured, helpful feedback.
    return f"""
    You are an expert code reviewer. Analyze the following code changes (in .diff format) and provide a concise, constructive review.

    Focus on:
    1.  **Potential Bugs:** Identify any logic errors or edge cases that might have been missed.
    2.  **Best Practices:** Suggest improvements based on language-specific best practices (e.g., Python PEP 8).
    3.  **Readability & Maintainability:** Comment on code clarity, naming conventions, and overall structure.
    4.  **Security Vulnerabilities:** Point out any potential security risks.

    Format your review in Markdown. Use headings and bullet points for clarity.
    If there are no issues, simply state: "Looks good to me! No issues found."

    Here is the diff:
    ```diff
    {diff}
    ```
    """

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "AI Code Review Assistant is running!"}

@app.post("/webhook")
async def github_webhook(request: Request):
    try:
        payload = await request.json()

        # We are only interested in pull requests that are newly opened or updated
        if "pull_request" not in payload or payload.get("action") not in ["opened", "synchronize"]:
            return {"status": "ignored", "reason": "Not a relevant pull request event"}

        # Extract necessary information from the payload
        pull_request = payload["pull_request"]
        diff_url = pull_request["diff_url"]
        comments_url = pull_request["comments_url"]

        print(f"Processing PR: {pull_request['html_url']}")

        # 1. Fetch the code changes (the diff)
        diff_content = await get_pull_request_diff(diff_url)
        print("Successfully fetched diff.")

        # 2. Generate the prompt for the AI
        prompt = generate_review_prompt(diff_content)

        # 3. Call the Gemini API to get the review
        print("Sending request to Gemini API...")
        response = model.generate_content(prompt)
        review_text = response.text
        print("Received review from Gemini.")

        # 4. Post the review back to GitHub
        await post_review_comment(comments_url, review_text)
        print(f"Successfully posted comment to PR: {pull_request['html_url']}")

        return {"status": "success"}

    except Exception as e:
        # Log the error for debugging
        print(f"An error occurred: {e}")
        # Raise an HTTPException to return a proper error response
        raise HTTPException(status_code=500, detail=str(e))
