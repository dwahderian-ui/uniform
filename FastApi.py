from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import hashlib
import uvicorn
import os

app = FastAPI(title="Uni-Form Backend API")

# --- Database Connection ---
# MongoDB is used as the primary database [cite: 104]
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.uniform_db


# --- Data Models ---
class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    role: str  # 'student' or 'secretary'


# --- 1. Authentication Route ---
@app.post("/login", response_model=UserResponse)
async def login(user_data: UserLogin):
    """
    Authenticates students and secretaries[cite: 42, 43].
    """
    user = await db.users.find_one({"username": user_data.username})

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Security: Using SHA-256 to mitigate data breach risks
    hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()

    if hashed_password != user['password']:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"username": user['username'], "role": user['role']}


# --- 2. Request Submission (Student) ---
@app.post("/submit-request")
async def submit_request(
        student_name: str = Form(...),
        course_name: str = Form(...),
        exam_date: str = Form(...),  # Format: YYYY-MM-DD
        file: UploadFile = File(...)  # Uploading "Tzav Miluim" [cite: 44, 79]
):
    """
    Allows students to submit a tutoring request with a military order[cite: 38, 45].
    """
    # Create the request document
    request_doc = {
        "student_name": student_name,
        "course": course_name,
        "exam_date": datetime.strptime(exam_date, "%Y-%m-%d"),
        "status": "pending",  # Initial status: pending [cite: 65]
        "file_name": file.filename,
        "created_at": datetime.now()
    }

    # Save to MongoDB
    result = await db.requests.insert_one(request_doc)

    return {"status": "success", "message": "Request submitted", "id": str(result.inserted_id)}


# --- 3. Prioritized Dashboard (Secretary) ---
@app.get("/admin/dashboard")
async def get_dashboard():
    """
    Returns prioritized requests for the secretary[cite: 39, 46].
    Urgent requests (exam within 14 days) are highlighted.
    """
    # Define urgency threshold (2 weeks)
    urgent_threshold = datetime.now() + timedelta(days=14)

    # Fetch all requests sorted by exam date
    cursor = db.requests.find().sort("exam_date", 1)
    requests = await cursor.to_list(length=100)

    for req in requests:
        req["_id"] = str(req["_id"])
        # Logic for automatic prioritization [cite: 49]
        req["is_urgent"] = req["exam_date"] <= urgent_threshold

    return requests


# --- 4. Update Status (Secretary) ---
@app.post("/admin/update-status")
async def update_status(request_id: str = Form(...), new_status: str = Form(...)):
    """
    Allows secretaries to approve/reject requests with one click[cite: 39, 46, 62].
    Supports immediate notification goal[cite: 65].
    """
    from bson import ObjectId

    await db.requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": new_status, "updated_at": datetime.now()}}
    )

    return {"status": "success", "new_status": new_status}


# --- Server Entry Point ---
if __name__ == "__main__":
    # Running on port 8001 to avoid common conflicts [cite: 99]
    uvicorn.run(app, host="0.0.0.0", port=8001)
