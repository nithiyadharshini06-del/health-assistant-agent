from flask import Flask, request, jsonify, render_template
from main import health_advice

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health", methods=["POST"])
def health():
    data = request.json
    symptoms = data.get("symptoms", "")

    try:
        result = health_advice(symptoms)
        return jsonify({"response": result})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"response": f"Server Error: {str(e)}"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)