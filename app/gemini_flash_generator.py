from .config import get_settings
from .gemini_client import get_client


def generate_nutrition_tip_with_flash(goal: str) -> str:
    client = get_client()
    settings = get_settings()

    # Safe fallback tips if Gemini is unavailable
    fallback_tips = {
        "weight loss":
            "Build meals around vegetables, protein, whole grains or other filling foods, and water. Avoid extreme restriction.",

        "muscle gain":
            "Include a protein-rich food with regular meals and eat enough overall to support training and recovery.",

        "general wellness":
            "Aim for balanced meals, enough water, fruits and vegetables, protein-rich foods, and consistent sleep.",

        "flexibility":
            "Support recovery with balanced meals, hydration, and enough overall energy rather than aggressive dieting.",
    }

    # Select a fallback based on the user's goal
    fallback = fallback_tips.get(
        goal,
        fallback_tips["general wellness"]
    )

    # If Gemini client is unavailable, use fallback
    if client is None:
        return fallback

    prompt = f"""
Give one concise nutrition or recovery tip
for someone whose fitness goal is:

{goal}

Requirements:

- Keep it general wellness guidance.
- Do not diagnose health conditions.
- Do not prescribe medication.
- Do not recommend extreme diets.
- Keep it practical.
- Maximum 4 sentences.

Return only the tip.
"""

    try:
        response = client.models.generate_content(
            model=settings.nutrition_model,
            contents=prompt,
        )

        text = getattr(response, "text", None)

        # If Gemini returns an empty response, use fallback
        if not text:
            return fallback

        return text.strip()

    # Handles temporary Gemini errors such as 503
    except Exception:
        return fallback