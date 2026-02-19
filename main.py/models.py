from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import hashlib


class InternshipPosting(BaseModel):
    """
    Data model representing a single internship posting.
    """

    id: str
    source: str
    company: str
    title: str
    location: str
    is_remote: bool
    url: str
    date_posted: Optional[datetime]
    scraped_at: datetime
    tags: List[str]

    def compute_id(self) -> str:
        """
        Generate a stable unique ID based on key fields.
        """
        raw_string = f"{self.source}|{self.company}|{self.title}|{self.url}"
        return hashlib.sha256(raw_string.encode()).hexdigest()