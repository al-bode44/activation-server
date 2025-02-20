from flask import Flask, request, jsonify

app = Flask(__name__)

# قائمة الأكواد المسموح بها
valid_keys = {"7943A11C538582AB3DED6BF0343C275B45132F9D6F476568B3FA89460C0B6D98"}  # يمكنك تخزينها في قاعدة بيانات لاحقًا

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
