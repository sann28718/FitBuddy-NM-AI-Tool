from .config import get_settings
from .gemini_client import get_client


def update_workout_plan(
    original_plan: str,
    feedback: str
) -> str:

    client = get_client()

    settings = get_settings()

    if client is None:

        return f"""
{original_plan}


UPDATED BASED ON USER FEEDBACK

User requested:

{feedback}

Please apply this change gradually while
keeping at least one recovery day.
"""

    prompt = f"""
You are FitBuddy.

Update the existing workout plan according
to the user's feedback.

ORIGINAL PLAN
----------------

{original_plan}

----------------


USER FEEDBACK
----------------

{feedback}

----------------


REQUIREMENTS

1. Keep the 7-day structure.
2. Apply the user's requested changes.
3. Keep training reasonable.
4. Include recovery/rest.
5. Avoid dangerous exercise recommendations.
6. Do not diagnose injuries or medical conditions.
7. If the feedback mentions concerning pain or injury,
   advise appropriate professional help instead of diagnosing it.

Return ONLY the revised workout plan.
"""

    response = client.models.generate_content(
        model=settings.workout_model,
        contents=prompt,
    )

    text = getattr(
        response,
        "text",
        None
    )

    if not text:

        raise RuntimeError(
            "Gemini returned an empty updated plan."
        )

    return text.strip()