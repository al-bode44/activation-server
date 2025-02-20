import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# قراءة الأكواد من متغير البيئة
valid_keys = set(os.getenv("VALID_KEYS", "").split(","))

@app.route("/verify", methods=["POST"])
def verify_key():
    data = request.json
    key = data.get("key")

    if key in valid_keys:
        return jsonify({"status": "success", "message": "✅ التفعيل ناجح!"})
    else:
        return jsonify({"status": "error", "message": "❌ كود التفعيل غير صحيح!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
