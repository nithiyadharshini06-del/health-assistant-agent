from flask import Flask, request, jsonify, render_template

# Local imports
from main import health_advice, clear_chat

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health", methods=["POST"])
def health():
    data = request.json
    symptoms = data.get("symptoms", "")
    session_id = data.get("session_id", "")
    image_base64 = data.get("image", None)

    if not session_id:
        return jsonify({"response": "Error: Missing session ID."}), 400

    try:
        result = health_advice(session_id, symptoms, image_base64)
        return jsonify({"response": result})
    except Exception as e:
        error_msg = str(e)
        import traceback
        traceback.print_exc()
        
        # Check if the error is a 429 Quota Exhausted error from Google
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return jsonify({"response": "**⚠️ Slow Down!**<br><br>The AI is currently receiving too many requests (Free Tier Limit). Please wait about 60 seconds and try again!"})
            
        return jsonify({"response": f"Server Error: {error_msg}"})

@app.route("/clear", methods=["POST"])
def clear():
    data = request.json
    session_id = data.get("session_id", "")
    if session_id:
        clear_chat(session_id)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)