from pydantic import BaseModel, Field


class CareInstructions(BaseModel):
    ideal_temperature: float = Field(description="Ideal temperature for the plant")
    lighting_level: str = Field(description="Adequate lightning level for the plant")
    watering_frequency: str = Field(
        description="How often should the plant be watered expressed in times per day or times per week")

    specific_diseases: list[str] = Field(description="What diseases the plant is most susceptible to")
    soil_type: str = Field(description="The ideal soil type for the plant")
    vase_type: str | None = Field(
        description="The ideal vase to grow the plant in, could be None if the plant should not be grown in a vase",
        default=None)


class PlantCareCard(BaseModel):
    latin_name: str = Field(description="The scientific name of the plant in question")
    common_name: str = Field(description="The common name of the plant in question")
    instructions: CareInstructions = Field(description="The care instructions for the plant")
