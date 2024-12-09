import datetime

from pydantic import BaseModel, Field, field_validator


class RatesParams(BaseModel):
    from_: str = Field("USD", examples=["USD", "RUB"], alias="from")
    to: str = Field("RUB", examples=["USD", "RUB"], alias="to")
    value: float = Field(100, gt=0)
    date: datetime.date = Field(datetime.date.today())

    @field_validator("from_", "to", mode="before")
    @classmethod
    def validate_to_and_from(cls, v: str) -> str:
        return v.upper()

    class Config:
        populate_by_name = True
