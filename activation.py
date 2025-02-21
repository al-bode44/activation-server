import os
import hashlib
import requests

SERVER_URL = "https://4dc1beb5-11ab-42f9-8ed1-1c4fa41037b5-00-2hb4o4xmha4tb.worf.replit.dev:8080/verify"
REGISTRY_PATH = r"Software\MyTool"
REGISTRY_KEY = "Activated"

def generate_activation_key():
    """Generates a fixed activation code for each device based on the device's UUID"""
    device_id = os.popen("wmic csproduct get UUID").read().strip().split("\n")[-1]  # Get the device UUID
    key = hashlib.sha256(device_id.encode()).hexdigest().upper()  # Encrypt the UUID and produce a fixed code
    return key[:]  # Select the first 16 characters only (can be changed as needed)

activation_key = generate_activation_key()
print(f"Activation Key: {activation_key}")

def activate():
    response = requests.post(SERVER_URL, json={"key": activation_key}).json()

    if response["status"] == "success":
        print("")
        
    else:
       input("🔹 Send the code to the administrator, and press Enter after receiving the activation...")
 

if __name__ == "_main_":
    activate()