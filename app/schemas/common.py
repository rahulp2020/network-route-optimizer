from datetime import datetime, timezone
from typing import Annotated

from pydantic import AfterValidator, Field


def clean_name(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("must not be empty or whitespace only")
    return cleaned


def to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


NodeName = Annotated[str, Field(max_length=255), AfterValidator(clean_name)]
Latency = Annotated[float, Field(gt=0, allow_inf_nan=False)]
