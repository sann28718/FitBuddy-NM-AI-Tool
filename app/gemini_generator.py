from .config import get_settings
from .gemini_client import get_client
from .schemas import UserInput


SYSTEM_INSTRUCTION = """
You are FitBuddy, an AI wellness workout planning assistant.

Create practical and age-appropriate general fitness guidance.

You must NOT:
- diagnose medical conditions
- prescribe medication
- claim to replace a doctor
- recommend dangerous exercise extremes
- recommend extreme dieting
- encourage exercising through pain

If the user mentions an injury, serious pain, fainting,
or another concerning symptom, recommend appropriate
professional help rather than trying to diagnose it.

Focus on safe, gradual, general wellness guidance.
"""


def fallback_plan(user: UserInput) -> str:

    return f"""
FITBUDDY 7-DAY FITNESS PLAN

User:
{user.username}

Goal:
{user.goal}

Preferred intensity:
{user.intensity}


DAY 1 - FULL BODY

Warm-up:
5-10 minutes of easy walking and mobility.

Workout:
Bodyweight Squats - 3 x 10
Incline Push-ups - 3 x 8
Glute Bridges - 3 x 12
Plank - 3 x 20 seconds

Cooldown:
5 minutes of gentle stretching.


DAY 2 - CARDIO + CORE

Warm-up:
5 minutes easy movement.

Workout:
Brisk Walking - 20-30 minutes
Dead Bug - 3 x 8 each side
Bird Dog - 3 x 8 each side

Cooldown:
Easy walking and gentle stretching.


DAY 3 - RECOVERY

Easy walking:
20-30 minutes.

Mobility:
10 minutes of comfortable mobility work.

Keep the effort easy.


DAY 4 - STRENGTH

Warm-up:
5-10 minutes.

Workout:
Split Squat - 3 x 8 each side
Incline Push-up - 3 x 10
Hip Hinge - 3 x 10
Side Plank - 2 x 15 seconds each side

Cooldown:
5 minutes.


DAY 5 - CARDIO

Warm-up:
5 minutes.

Workout:
20-30 minutes moderate cardio.

Keep a comfortable pace.

Cooldown:
5 minutes easy walking.


DAY 6 - FULL BODY + CORE

Warm-up:
5-10 minutes.

Workout:
Squats - 3 x 10
Push-ups - 3 x 8
Glute Bridges - 3 x 12
Plank - 3 x 20 seconds

Cooldown:
5 minutes.


DAY 7 - REST / ACTIVE RECOVERY

Easy walking and gentle mobility.

Focus on recovery and sleep.


SAFETY NOTE

Start gradually and stop if an exercise causes
pain or unusual symptoms.
"""


def generate_workout_gemini(
    user: UserInput
) -> str:

    client = get_client()

    settings = get_settings()

    if client is None:

        return fallback_plan(user)

    prompt = f"""
{SYSTEM_INSTRUCTION}

Create a personalized 7-day fitness plan.

USER INFORMATION

Name:
{user.username}

Age:
{user.age}

Weight:
{user.weight} kg

Fitness goal:
{user.goal}

Preferred intensity:
{user.intensity}


REQUIREMENTS

Create Day 1 through Day 7.

For every workout day provide:

1. Warm-up
2. Main workout
3. Exercise names
4. Sets and repetitions OR duration
5. Rest guidance
6. Cooldown/recovery

Include at least one recovery/rest day.

The plan should be practical and progressive.

Do not recommend extreme training.

Do not diagnose medical conditions.

Return only the workout plan.
"""

    try:
        response = client.models.generate_content(
            model=settings.workout_model,
            contents=prompt,
        )
    except Exception:
        return fallback_plan(user)

    text = getattr(
        response,
        "text",
        None
    )

    if not text:
        return fallback_plan(user)

    return text.strip()