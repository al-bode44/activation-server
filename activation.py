import os
import hashlib
import requests
import winreg  # مكتبة التعامل مع الريجستري

SERVER_URL = "http://127.0.0.1:5000/verify"
REGISTRY_PATH = r"Software\MyTool"
REGISTRY_KEY = "Activated"
import uuid
import hashlib
import os

def generate_activation_key():
    """يولد كود تفعيل ثابت لكل جهاز بناءً على UUID الخاص بالجهاز"""
    device_id = os.popen("wmic csproduct get UUID").read().strip().split("\n")[-1]  # الحصول على UUID الجهاز
    key = hashlib.sha256(device_id.encode()).hexdigest().upper()  # تشفير UUID وإنتاج كود ثابت
    return key[:]  # اختيار أول 16 حرف فقط (يمكن تغييره حسب الحاجة)

activation_key = generate_activation_key()
print(f"Activation Key: {activation_key}")

def is_activated():
    """يتحقق مما إذا كان الجهاز مفعّل عبر الريجستري"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_PATH, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, REGISTRY_KEY)
            return value == "1"
    except FileNotFoundError:
        return False

def set_activated():
    """يحفظ حالة التفعيل في الريجستري"""
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_PATH) as key:
        winreg.SetValueEx(key, REGISTRY_KEY, 0, winreg.REG_SZ, "1")

def activate():
    """يفحص إذا كان الجهاز مفعّل أم لا"""
    if is_activated():
        print("✅ الأداة مفعّلة بالفعل!")
        return

    # activation_key = generate_activation_key()
    # print(f"🔑 كود التفعيل الخاص بجهازك: {activation_key}")
    input("🔹 أرسل الكود للمسؤول، واضغط Enter بعد الحصول على التفعيل...")

    response = requests.post(SERVER_URL, json={"key": activation_key}).json()

    if response["status"] == "success":
        print("✅ تم التفعيل بنجاح!")
        set_activated()
    else:
        print("❌ كود التفعيل غير صالح. حاول مرة أخرى!")

if __name__ == "__main__":
    activate()
