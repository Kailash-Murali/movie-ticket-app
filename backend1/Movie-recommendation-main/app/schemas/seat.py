from pydantic import BaseModel, ConfigDict

class SeatBase(BaseModel):
    id: str
    show_id: str
    row: str
    number: int
    seat_code: str
    type: str
    status: str
    price: int

    model_config = ConfigDict(from_attributes=True)

class SeatResponse(SeatBase):
    pass
