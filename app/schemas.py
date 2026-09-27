from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


ALLOWED_GOALS = {
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
}


ALLOWED_INTENSITIES = {
    "low",
    "medium",
    "high",
}


class UserInput(BaseModel):

    username: str = Field(
        min_length=1,
        max_length=120
    )

    user_id: str = Field(
        min_length=1,
        max_length=80
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight: float = Field(
        gt=0,
        le=500
    )

    goal: str = Field(
        min_length=2,
        max_length=50
    )

    intensity: str = Field(
        min_length=2,
        max_length=20
    )

    @field_validator(
        "username",
        "user_id",
        "goal",
        "intensity"
    )
    @classmethod
    def clean_text(cls, value):

        value = value.strip()

        if not value:
            raise ValueError(
                "This field cannot be empty."
            )

        return value

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, value):

        value = value.lower().strip()

        if value not in ALLOWED_GOALS:

            raise ValueError(
                "Invalid fitness goal."
            )

        return value

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, value):

        value = value.lower().strip()

        if value not in ALLOWED_INTENSITIES:

            raise ValueError(
                "Intensity must be low, medium, or high."
            )

        return value


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=1,
        max_length=80
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000
    )

    @field_validator(
        "user_id",
        "feedback"
    )
    @classmethod
    def clean_text(cls, value):

        return value.strip()