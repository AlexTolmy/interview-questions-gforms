from abc import ABC, abstractmethod
from typing import List, Optional

from .dto import FromInfo, Question, Theme


class StorageDrive(ABC):

    @abstractmethod
    def delete(self, _id: str):
        ...


class StorageForm(ABC):

    @abstractmethod
    def create(self, title: str, form_title: str) -> FromInfo:
        ...

    @abstractmethod
    def create_questions(self, _id: str, questions: List[Question]):
        ...

    @abstractmethod
    def create_description(self, _id: str, description: str):
        ...


class StorageSheet(ABC):

    @abstractmethod
    def get(self) -> List[Theme]:
        ...
