from pydantic import BaseModel


class ConstraintViolation(BaseModel):
    constraint: str
    message: str
    required: str | None = None
    available: str | None = None


class ConstraintEvaluationResult(BaseModel):
    valid: bool
    violations: list[ConstraintViolation] = []