from typing import TypedDict, Optional

from PIL.Image import Image

from server.model.PlantCareCard import PlantCareCard


class AgentState(TypedDict):
    image_buffer: Optional[Image]
    plant_name: Optional[str]
    plant_card: Optional[PlantCareCard]
    article: Optional[str]
    web_knowledge: Optional[str]
    internal_knowledge: Optional[str]
