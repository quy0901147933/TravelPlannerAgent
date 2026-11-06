from datetime import date, timedelta
from pydantic import BaseModel , Field , field_validator , model_validator
from typing import Literal

class TravelPreferences(BaseModel):
    duration_days: int = Field(ge=2 , le=7)
    origin_city: str = Field(min_length=1)
    destination_city: Literal["Paris" , "Strasbourg" , "Lyon"]
    departure_day: date
    num_adults: int  = Field(gt=0)
    additional_preferences: str | None = Field(default=None , max_length=1000)
    total_budget_eur: int = Field(gt=0)

    @field_validator("origin_city" , "destination_city" , mode="before")
    @classmethod

    def strip_name_city(cls , value):
        if isinstance(value , str):
            return value.strip()
        return value

    @field_validator("additional_preferences" , mode="before")
    @classmethod

    def normalize_preferences(cls , value):
        if isinstance(value , str):
            return value.strip() or None 
        return value
    
    @field_validator("departure_day")
    @classmethod
    def validate_departure_day(cls , value: date) -> date:
        if value < date.today():
           raise ValueError("Departure Day cannot be date in the past")
        return value

    @model_validator(mode="after")
    def validate_difference_cities(self):
        if self.origin_city.casefold() == self.destination_city.casefold():
           raise ValueError("Origin city must be different with destination city !")
        return self 
    @property
    def return_date(self) -> date:
        return self.departure_day + timedelta(days=self.duration_days - 1)

    
    

    



