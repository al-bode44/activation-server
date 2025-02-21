import traceback
from flask import Flask, request, jsonify

app = Flask(__name__)

CODES_FILE = "codes.txt"

# وظيفة لتحميل الأكواد من ملف نصي
def load_codes():
    try:
        with open(CODES_FILE, "r") as file:
            return {line.strip("'''") for line in file.readlines()}  # تحويل الأكواد إلى set لتسريع البحث
    except FileNotFoundError:
        return set()  # إرجاع قائمة فارغة لو الملف غير موجود

# وظيفة لحفظ الأكواد في ملف نصي
def save_code(new_code):
    with open(CODES_FILE, "a") as file:  # استخدام append بدلاً من الكتابة الكاملة
        file.write(new_code + ",")

@app.route('/add_code', methods=['POST'])
def add_code():
    try:
        new_code = request.data.decode("utf-8").strip()
        # new_code = data.get("code")

        if not new_code:
            return jsonify({"status": "error", "message": "No code provided"}), 400

        codes = load_codes()

        if new_code in codes:
            return jsonify({"status": "error", "message": "Code already exists"}), 400

        save_code(new_code)  # حفظ الكود الجديد في الملف

        return jsonify({"status": "success", "message": "Code added successfully"}), 200

    except Exception as e:
        print("❌ خطأ في السيرفر:", e)
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500

@app.route("/verify", methods=["POST"])
def verify_key():

    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "❌ لم يتم إرسال بيانات صحيحة!"}), 400

        key = data.get("key")
        codes =  load_codes()
        verify_key = str(codes).replace("'", '')


        if key in verify_key:
            return jsonify({"status": "success", "message": "✅ التفعيل ناجح!"}), 200
        else:
            return jsonify({"status": "error", "message": "❌ كود التفعيل غير صحيح!"}), 400

    except Exception as e:
        print("❌ خطأ في السيرفر:", e)
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500

@app.route('/')
def keep_alive():
    return "Server is alive!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
