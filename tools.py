from main import client, save_study_plan

def calculator(hours_per_day, days):
    total_hours = hours_per_day * days

    return {
        "hours_per_day": hours_per_day,
        "days": days,
        "total_hours": total_hours
    }


def planner(subject, days, hours_per_day):
    prompt = f"""
    You are StudyPilot, an AI study planning assistant.

    Create a simple and practical study plan.

    Subject: {subject}
    Number of days: {days}
    Hours available per day: {hours_per_day}

    Requirements:
    1. Create a day-by-day plan.
    2. Divide the available study time properly.
    3. Include topics to study each day.
    4. Include revision when appropriate.
    5. Keep the plan realistic for a student.
    6. Use simple language.

    Format the answer clearly as:

    Day 1:
    - Topic:
    - Study time:
    - Task:

    Day 2:
    - Topic:
    - Study time:
    - Task:

    Continue until Day {days}.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text

def save_plan(student_id, subject, days, hours_per_day, study_plan):
    save_study_plan(
        student_id=student_id,
        subject=subject,
        days=days,
        hours_per_day=hours_per_day,
        study_plan=study_plan
    )

    return {
        "status": "success",
        "message": "Study plan saved successfully"
    }

if __name__ == "__main__":
    print("Testing Calculator:")
    print(calculator(3, 7))

    print("\nTesting Planner:")
    plan = planner("Python", 5, 3)
    print(plan)

    print("\nTesting Database:")
    result = save_plan(
        student_id=1,
        subject="Agent Test",
        days=2,
        hours_per_day=2,
        study_plan=plan
    )
    print(result)