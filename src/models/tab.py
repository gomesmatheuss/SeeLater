from datetime import datetime
from dataclasses import dataclass
from typing import List

@dataclass
class Tab:
    url: str
    title: str
    index: int
    priority: str
    create_at: datetime
    tags: List[str] = None
    active: bool = True

    def __post_init__(self):
        if self.tags is None:
            self.tags = []