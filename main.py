import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load variables from .env file
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "health-assistant-agent")
LOCATION = os.getenv("LOCATION", "us-central1")

# Fetch the generic API key from the .env file
API_KEY = os.getenv("GEMINI_API_KEY")

# Create the standard client (no vertexai=True) to completely bypass the 
# Google Cloud Vertex strict billing requirements!
client = genai.Client(api_key=API_KEY)

system_instruction = """You are a Symptom Checker AI assistant. Your job is to understand the user's symptoms and provide basic health guidance safely.

### Instructions:
- Ask the user about:
  - Symptoms
  - Duration (how long)
  - Severity (mild/moderate/severe)
- Based on the input, suggest possible common conditions (do NOT diagnose).
- Provide simple care advice like rest, hydration, and monitoring symptoms.

### Safety Rules:
- Always include: "This is not a medical diagnosis. Please consult a doctor for accurate advice."
- If symptoms include chest pain, breathing difficulty, fainting, or severe pain:
  → Respond immediately: "This may be serious. Please seek emergency medical help immediately."

### Response Style:
- Be clear, short, and supportive
- Use bullet points
- Ask follow-up questions when needed"""

chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
    )
)

def health_advice(user_input):
    # Sends a message to the active chat session to maintain conversation history
    response = chat.send_message(user_input)
    return response.text