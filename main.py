import os
import io
import base64
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load variables from .env file
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "health-assistant-agent")
LOCATION = os.getenv("LOCATION", "us-central1")
API_KEY = os.getenv("GEMINI_API_KEY")

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
- Use bullet points and markdown formatting (bold, headers)
- Ask follow-up questions when needed"""

ACTIVE_SESSIONS = {}

def get_or_create_chat(session_id):
    if session_id not in ACTIVE_SESSIONS:
        ACTIVE_SESSIONS[session_id] = client.chats.create(
            model="gemini-1.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
            )
        )
    return ACTIVE_SESSIONS[session_id]

def clear_chat(session_id):
    if session_id in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[session_id]

def health_advice(session_id, user_input, image_base64=None):
    chat = get_or_create_chat(session_id)
    contents = []
    
    if user_input and user_input.strip():
        contents.append(user_input)
        
    if image_base64:
        try:
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]
            image_data = base64.b64decode(image_base64)
            img = Image.open(io.BytesIO(image_data))
            contents.append(img)
            
            # If no manual text was provided, provide a default prompt for the image
            if not user_input or not user_input.strip():
                contents.append("Please analyze this medical-related image regarding my symptoms.")
        except Exception as e:
            print(f"Error decoding image: {e}")
            contents.append("[System: Failed to process attached image]")

    if not contents:
        return "I didn't receive any input. How can I help you?"

    response = chat.send_message(contents)
    return response.text