from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Question:
    text: str
    image_url: Optional[str]


@dataclass
class InfoUpdate:
    _id: str
    update_form_info: str


@dataclass
class Theme:
    title: str
    questions: List[Question] = field(default_factory=lambda: [])


@dataclass
class FromInfo:
    id: str
    view_form_url: str
    response_url: str
