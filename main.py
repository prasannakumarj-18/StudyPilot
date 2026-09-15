from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()
import json
# -------------------------
# PostgreSQL Database
# -------------------------
connection = psycopg2.connect(
    os.getenv("DATABASE_URL")
)

print("PostgreSQL Database connected successfully!")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://prasannakumarj-18.github.io"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------------------------
# Gemini API
# -------------------------
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -------------------------
# Home
# -------------------------
@app.get("/")
def home():
    return {
        "message": "StudyPilot API is running"
    }

# -------------------------
# Student
# -------------------------
@app.get("/student")
def student():
    return {
        "name": "SAI",
        "age": 20,
        "branch": "AIML"
    }

# -------------------------
# Test AI
# -------------------------
@app.get("/test-ai")
def test_ai():
    return {
        "message": "StudyPilot Gemini AI endpoint is ready"
    }

# -------------------------
# Student Request Model
# -------------------------
class StudentRequest(BaseModel):
    subject: str
    days: int
    hours_per_day: float

# -------------------------
# Save Study Plan
# -------------------------
def save_study_plan(
    student_id: int,
    subject: str,
    days: int,
    hours_per_day: float,
    study_plan: str
):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO study_plans
        (student_id, subject, days, hours_per_day, study_plan)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        student_id,
        subject,
        days,
        hours_per_day,
        study_plan
    ))

    plan_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()

    return plan_id

# -------------------------
# Create Progress Records
# -------------------------
def create_progress_records(plan_id: int, days: int):
    cursor = connection.cursor()

    for day_number in range(1, days + 1):
        cursor.execute("""
            INSERT INTO study_progress
            (study_plan_id, day_number, status)
            VALUES (%s, %s, %s)
        """, (
            plan_id,
            day_number,
            "PENDING"
        ))

    connection.commit()
    cursor.close()
# -------------------------
# Create Study Plan
# -------------------------
# -------------------------
# Mark Day as Completed
# -------------------------
@app.put("/progress/{plan_id}/{day_number}")
def complete_day(plan_id: int, day_number: int):

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE study_progress
        SET status = 'COMPLETED',
            completed_at = CURRENT_TIMESTAMP
        WHERE study_plan_id = %s
        AND day_number = %s
    """, (
        plan_id,
        day_number
    ))

    connection.commit()
    cursor.close()

    return {
        "message": "Day completed successfully",
        "study_plan_id": plan_id,
        "day_number": day_number,
        "status": "COMPLETED"
    }
# -------------------------
# Get Study Progress
# -------------------------
@app.get("/progress/{plan_id}")
def get_progress(plan_id: int):

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_days,
            SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_days
        FROM study_progress
        WHERE study_plan_id = %s
    """, (plan_id,))

    total_days, completed_days = cursor.fetchone()

    cursor.close()

    if total_days == 0:
        return {
            "message": "No progress records found"
        }

    progress_percentage = (completed_days / total_days) * 100

    return {
        "study_plan_id": plan_id,
        "total_days": total_days,
        "completed_days": completed_days,
        "progress_percentage": progress_percentage
    }
# -------------------------
# Progress Details
# -------------------------
@app.get("/progress-details/{plan_id}")
def get_progress_details(plan_id: int):

    cursor = connection.cursor()

    cursor.execute("""
        SELECT day_number, status, completed_at
        FROM study_progress
        WHERE study_plan_id = %s
        ORDER BY day_number
    """, (plan_id,))

    rows = cursor.fetchall()

    cursor.close()

    total_days = len(rows)
    completed_days = sum(
        1 for row in rows
        if row[1] == "COMPLETED"
    )

    progress_percentage = 0

    if total_days > 0:
        progress_percentage = round(
            (completed_days / total_days) * 100,
            2
        )

    return {
        "study_plan_id": plan_id,
        "total_days": total_days,
        "completed_days": completed_days,
        "progress_percentage": progress_percentage,
        "days": [
            {
                "day_number": row[0],
                "status": row[1],
                "completed_at": row[2]
            }
            for row in rows
        ]
    }
@app.get("/studyplan/{plan_id}")
def get_study_plan(plan_id: int):

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            subject,
            days,
            hours_per_day,
            study_plan
        FROM study_plans
        WHERE id = %s
    """, (plan_id,))

    row = cursor.fetchone()

    cursor.close()

    if row is None:
        return {
            "message": "Study plan not found"
        }

    # Convert Oracle CLOB into normal Python string
    study_plan = row[4]

    return {
        "plan_id": row[0],
        "subject": row[1],
        "days": row[2],
        "hours_per_day": row[3],
        "study_plan": study_plan
    }
@app.post("/studyplan")
def create_study_plan(request: StudentRequest):

    prompt = f"""
    You are StudyPilot, an AI study planning assistant.

    Create a study plan using EXACTLY these inputs:

    Subject: {request.subject}
    Number of days: {request.days}
    Hours per day: {request.hours_per_day}

STRICT RULES — YOU MUST FOLLOW THESE:
1. Generate EXACTLY {request.days} days. No more and no fewer.
2. Every day MUST contain exactly {request.hours_per_day} hours of study time.
3. Do NOT change the number of days.
4. Do NOT change the daily study hours.
5. Do NOT create extra days.
6. Divide the subject topics across exactly {request.days} days.
7. Include revision and practice where appropriate.
8. Use simple language.

    Use this exact JSON structure:

    {{
      "days": [
        {{
          "day": 1,
          "topic": "Topic name",
          "study_time": {request.hours_per_day},
          "task": "Task description"
        }}
      ]
    }}

    IMPORTANT:
    - Return ONLY valid JSON.
    - Do not use Markdown.
    - Generate exactly {request.days} day objects.
    - Every "study_time" must be exactly {request.hours_per_day}.
    - The "day" values must start at 1 and continue until {request.days}.
"""

    # Generate plan using Gemini
    response = client.models.generate_content(
      model="gemini-3.5-flash",
      contents=prompt,
      config={
        "response_mime_type": "application/json"
      }
    )

    plan = json.loads(response.text)

    # Validate AI-generated plan
    if len(plan["days"]) != request.days:
      raise ValueError("AI generated incorrect number of days")

    for day in plan["days"]:
      if day["study_time"] != request.hours_per_day:
        raise ValueError("AI generated incorrect study hours")

    for index, day in enumerate(plan["days"], start=1):
      if day["day"] != index:
        raise ValueError("AI generated incorrect day numbers")
        
    # Save generated plan to Oracle
    plan_id = save_study_plan(
       student_id=1,
       subject=request.subject,
       days=request.days,
       hours_per_day=request.hours_per_day,
       study_plan=json.dumps(plan)
    )
    create_progress_records(plan_id, request.days)

    return {
    "plan_id": plan_id,
    "subject": request.subject,
    "days": request.days,
    "hours_per_day": request.hours_per_day,
    "study_plan": response.text
}
