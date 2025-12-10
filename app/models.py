from typing import List, Optional
from pydantic import BaseModel, Field

class Activity(BaseModel):
    time: str = Field(..., description="Time of the activity (e.g., '09:00', '14:30', 'Morning').")
    activity: str = Field(..., description="Description of the activity.")
    place_name: Optional[str] = Field(None, description="Name of the place (restaurant, hotel, attraction) if applicable.")
    cost: Optional[float] = Field(None, description="Estimated cost if available.")
    
class DayPlan(BaseModel):
    day: int = Field(..., description="Day number of the trip.")
    city: str = Field(..., description="City for this day.")
    activities: List[Activity] = Field(..., description="List of activities for the day.")

class Itinerary(BaseModel):
    title: str = Field(..., description="Title of the trip (e.g. '3-Day Trip to London').")
    total_cost: Optional[float] = Field(None, description="Total estimated cost.")
    days: List[DayPlan] = Field(..., description="Daily itinerary.")
    
    def to_markdown(self) -> str:
        md = f"# {self.title}\n"
        if self.total_cost:
            md += f"**Total Estimated Cost:** ${self.total_cost}\n\n"
        
        for day in self.days:
            md += f"## Day {day.day} - {day.city}\n"
            for act in day.activities:
                md += f"- **{act.time}**: {act.activity}"
                if act.place_name:
                    md += f" (@ {act.place_name})"
                md += "\n"
            md += "\n"
        return md
