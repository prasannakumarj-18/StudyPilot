from google.genai import types
from tools import calculator, planner, save_plan
from main import client


# -------------------------
# Tool Definitions
# -------------------------

calculator_tool = types.FunctionDeclaration(
    name="calculator",
    description="Calculate the total available study hours.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "hours_per_day": types.Schema(
                type="NUMBER",
                description="Study hours available per day"
            ),
            "days": types.Schema(
                type="INTEGER",
                description="Number of study days"
            )
        },
        required=["hours_per_day", "days"]
    )
)


planner_tool = types.FunctionDeclaration(
    name="planner",
    description="Create a practical day-by-day study plan.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "subject": types.Schema(
                type="STRING",
                description="Subject to study"
            ),
            "days": types.Schema(
                type="INTEGER",
                description="Number of study days"
            ),
            "hours_per_day": types.Schema(
                type="NUMBER",
                description="Study hours per day"
            )
        },
        required=["subject", "days", "hours_per_day"]
    )
)


save_plan_tool = types.FunctionDeclaration(
    name="save_plan",
    description="Save a study plan into the database.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "student_id": types.Schema(
                type="INTEGER",
                description="Student ID"
            ),
            "subject": types.Schema(
                type="STRING",
                description="Subject name"
            ),
            "days": types.Schema(
                type="INTEGER",
                description="Number of study days"
            ),
            "hours_per_day": types.Schema(
                type="NUMBER",
                description="Study hours per day"
            ),
            "study_plan": types.Schema(
                type="STRING",
                description="Generated study plan"
            )
        },
        required=[
            "student_id",
            "subject",
            "days",
            "hours_per_day",
            "study_plan"
        ]
    )
)


tools = types.Tool(
    function_declarations=[
        calculator_tool,
        planner_tool,
        save_plan_tool
    ]
)


# -------------------------
# Execute Tool
# -------------------------

def execute_tool(name, args):

    if name == "calculator":
        return calculator(
            hours_per_day=args["hours_per_day"],
            days=args["days"]
        )

    elif name == "planner":
        return planner(
            subject=args["subject"],
            days=args["days"],
            hours_per_day=args["hours_per_day"]
        )

    elif name == "save_plan":
        return save_plan(
            student_id=args["student_id"],
            subject=args["subject"],
            days=args["days"],
            hours_per_day=args["hours_per_day"],
            study_plan=args["study_plan"]
        )

    return {"error": f"Unknown tool: {name}"}


# -------------------------
# StudyPilot Agent
# -------------------------

def study_agent(user_request):

    contents = [user_request]

    while True:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                tools=[tools]
            )
        )

        tool_results = []

        for part in response.candidates[0].content.parts:

            if part.function_call:

                name = part.function_call.name
                args = dict(part.function_call.args)

                print(f"\nGemini requested:")
                print(f"- {name} → {args}")

                result = execute_tool(name, args)

                if isinstance(result, str):
                    result = {"result": result}

                tool_results.append(
                    types.Part.from_function_response(
                        name=name,
                        response=result
                    )
                )

        # No more tools requested = final answer
        if not tool_results:
            return response

        # Add Gemini's tool-call response
        contents.append(response.candidates[0].content)

        # Add tool results
        contents.append(
            types.Content(
                role="user",
                parts=tool_results
            )
        )
# -------------------------
# Test
# -------------------------

if __name__ == "__main__":

    request = """
    Create a 5-day Python study plan.
    I can study 3 hours per day.

    Calculate my total study hours,
    create the study plan,
    and save it to the database.
    """

    result = study_agent(request)

    print("\n--- StudyPilot Final Response ---")

    print(result.text)