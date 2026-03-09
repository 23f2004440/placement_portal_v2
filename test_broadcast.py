import requests
import json

base_url = "http://localhost:5000/api"

# Login as Admin
login_res = requests.post(
    f"{base_url}/auth/login",
    json={"username": "admin", "password": "admin123"}
)

if login_res.status_code == 200:
    token = login_res.json()['access_token']
    
    # Send Broadcast
    broadcast_res = requests.post(
        f"{base_url}/admin/broadcast-email",
        json={"subject": "Testing Broadcast System", "body": "This is a broadcast email sent from the Admin dashboard script."},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print("Broadcast Response:", broadcast_res.json())
else:
    print("Admin Login failed:", login_res.json())
