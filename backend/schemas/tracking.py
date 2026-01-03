from pydantic import BaseModel
from typing import Optional


class PageVisitCreate(BaseModel):
    session_id: str
    traffic_source: str
    referrer_url: Optional[str] = None
    user_agent: Optional[str] = None
    landing_page: Optional[str] = None
    ip_address: Optional[str] = None


class CalendlyClickCreate(BaseModel):
    session_id: str
    traffic_source: str
    button_id: Optional[str] = None
    button_location: Optional[str] = None
    page_url: Optional[str] = None
    via_whatsapp: bool=False


class CalendlyWebhook(BaseModel):
    event: str
    payload: dict