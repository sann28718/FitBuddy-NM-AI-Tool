from pathlib import Path

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash
)
from .gemini_generator import (
    generate_workout_gemini
)
from .models import User
from .schemas import (
    FeedbackRequest,
    UserInput
)
from .updated_plan import (
    update_workout_plan
)


BASE_DIR = Path(__file__).resolve().parent.parent


templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)


router = APIRouter()


# =========================================================
# HOME PAGE
# =========================================================

@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,

        name="index.html",

        context={
            "title":
                "FitBuddy - AI Fitness Plan Generator"
        }
    )


# =========================================================
# GENERATE WORKOUT
# =========================================================

@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(

    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        user_input = UserInput(

            username=username,

            user_id=user_id,

            age=age,

            weight=weight,

            goal=goal,

            intensity=intensity,
        )

    except Exception as exc:

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context={

                "title": "FitBuddy",

                "error": str(exc),

                "form": {

                    "username": username,

                    "user_id": user_id,

                    "age": age,

                    "weight": weight,

                    "goal": goal,

                    "intensity": intensity,
                },
            },

            status_code=
                status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


    existing_user = db.scalar(

        select(User).where(
            User.user_id ==
            user_input.user_id
        )

    )


    if existing_user:

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context={

                "title": "FitBuddy",

                "error":
                    f"User ID '{user_input.user_id}' "
                    "already exists.",

                "form":
                    user_input.model_dump(),
            },

            status_code=
                status.HTTP_409_CONFLICT,
        )


    try:

        # Generate workout

        workout_plan = (
            generate_workout_gemini(
                user_input
            )
        )


        # Generate nutrition tip

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                user_input.goal
            )
        )


        # Create database record

        user = User(

            user_id=user_input.user_id,

            username=user_input.username,

            age=user_input.age,

            weight=user_input.weight,

            goal=user_input.goal,

            intensity=user_input.intensity,

            original_plan=workout_plan,

            nutrition_tip=nutrition_tip,
        )


        db.add(user)

        db.commit()

        db.refresh(user)


    except Exception as exc:

        db.rollback()

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context={

                "title": "FitBuddy",

                "error":
                    f"Could not generate plan: {exc}",

                "form":
                    user_input.model_dump(),
            },

            status_code=
                status.HTTP_502_BAD_GATEWAY,
        )


    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context={

            "title":
                "Your FitBuddy Plan",

            "user":
                user,

            "plan":
                user.original_plan,

            "updated":
                False,
        }
    )


# =========================================================
# SUBMIT FEEDBACK
# =========================================================

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = FeedbackRequest(

            user_id=user_id,

            feedback=feedback
        )

    except Exception as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )


    user = db.scalar(

        select(User).where(
            User.user_id ==
            data.user_id
        )

    )


    if user is None:

        raise HTTPException(

            status_code=404,

            detail="User not found."
        )


    try:

        revised_plan = (
            update_workout_plan(

                user.original_plan,

                data.feedback
            )
        )


        user.updated_plan = revised_plan

        user.feedback = data.feedback


        db.commit()

        db.refresh(user)


    except Exception as exc:

        db.rollback()

        raise HTTPException(

            status_code=502,

            detail=
                f"Could not update plan: {exc}"
        )


    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context={

            "title":
                "Updated FitBuddy Plan",

            "user":
                user,

            "plan":
                user.updated_plan,

            "updated":
                True,
        }
    )


# =========================================================
# ADMIN VIEW
# =========================================================

@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(

    request: Request,

    db: Session = Depends(get_db)
):

    users = db.scalars(

        select(User)
        .order_by(
            User.created_at.desc()
        )

    ).all()


    return templates.TemplateResponse(

        request=request,

        name="all_users.html",

        context={

            "title":
                "FitBuddy Admin",

            "users":
                users
        }
    )


# =========================================================
# API HEALTH
# =========================================================

@router.get("/api/health")
def health():

    return {

        "status":
            "ok",

        "service":
            "FitBuddy"
    }


# =========================================================
# API GENERATE WORKOUT
# =========================================================

@router.post(
    "/api/generate-workout"
)
def api_generate_workout(

    data: UserInput,

    db: Session = Depends(get_db)
):

    existing_user = db.scalar(

        select(User).where(
            User.user_id ==
            data.user_id
        )
    )


    if existing_user:

        raise HTTPException(

            status_code=409,

            detail=
                "User ID already exists."
        )


    try:

        workout_plan = (
            generate_workout_gemini(
                data
            )
        )


        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                data.goal
            )
        )


        user = User(

            user_id=data.user_id,

            username=data.username,

            age=data.age,

            weight=data.weight,

            goal=data.goal,

            intensity=data.intensity,

            original_plan=workout_plan,

            nutrition_tip=nutrition_tip,
        )


        db.add(user)

        db.commit()

        db.refresh(user)


    except Exception as exc:

        db.rollback()

        raise HTTPException(

            status_code=502,

            detail=str(exc)
        )


    return {

        "message":
            "Plan generated successfully.",

        "user_id":
            user.user_id,

        "plan":
            user.original_plan,

        "nutrition_tip":
            user.nutrition_tip,
    }


# =========================================================
# API FEEDBACK
# =========================================================

@router.post(
    "/api/submit-feedback"
)
def api_submit_feedback(

    data: FeedbackRequest,

    db: Session = Depends(get_db)
):

    user = db.scalar(

        select(User).where(
            User.user_id ==
            data.user_id
        )
    )


    if user is None:

        raise HTTPException(

            status_code=404,

            detail="User not found."
        )


    try:

        revised_plan = (
            update_workout_plan(

                user.original_plan,

                data.feedback
            )
        )


        user.updated_plan = revised_plan

        user.feedback = data.feedback


        db.commit()

        db.refresh(user)


    except Exception as exc:

        db.rollback()

        raise HTTPException(

            status_code=502,

            detail=str(exc)
        )


    return {

        "message":
            "Plan updated successfully.",

        "user_id":
            user.user_id,

        "updated_plan":
            user.updated_plan
    }


# =========================================================
# API GET USERS
# =========================================================

@router.get(
    "/api/users"
)
def api_users(

    db: Session = Depends(get_db)
):

    users = db.scalars(

        select(User)
        .order_by(
            User.created_at.desc()
        )

    ).all()


    return [

        {

            "user_id":
                user.user_id,

            "username":
                user.username,

            "age":
                user.age,

            "weight":
                user.weight,

            "goal":
                user.goal,

            "intensity":
                user.intensity,

            "original_plan":
                user.original_plan,

            "updated_plan":
                user.updated_plan,

            "feedback":
                user.feedback,

            "created_at":
                user.created_at,

            "updated_at":
                user.updated_at,
        }

        for user in users
    ]