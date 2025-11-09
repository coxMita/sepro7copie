from datetime import datetime

from pydantic import BaseModel


class OccupancyUpdateRequest(BaseModel):
    """DTO for occupancy update request.

    Attributes:
        desk_id (str): Identifier of the desk.
        occupied (bool): Whether the desk is occupied.
        timestamp (datetime): When the occupancy state was recorded.

    """

    desk_id: str
    occupied: bool
    timestamp: datetime
