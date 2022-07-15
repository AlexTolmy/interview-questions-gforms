import datetime
import logging
import random
from typing import List, Optional

from classic.components import component
from pydantic import validate_arguments

from . import interfaces
from .dto import Question, Theme


@component
class Forms:
    drive_resource: interfaces.StorageDrive
    form_resource: interfaces.StorageForm
    sheet_resource: interfaces.StorageSheet

    def __attrs_post_init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @validate_arguments
    def run(self, candidate_name: str):
        themes = self.sheet_resource.get()
        form_info = self.form_resource.create(
            title='На вопросы необходимо ответить в течении 10 минут',
            form_title=f'Вопросы для {candidate_name}, {datetime.datetime.now()}'
        )
        questions = self._make_questions(themes=themes)
        self.logger.info('Сформированы вопросы: %s', questions)
        if len(questions) > 0:
            self.form_resource.create_questions(
                _id=form_info.id, questions=questions
            )

        self.logger.info(form_info.view_form_url)
        self.logger.info(form_info.response_url)
        self.logger.info(f'Id формы: %s', form_info.id)
        self.logger.info('Введите что то для продолжения')
        input()
        self.drive_resource.delete(_id=form_info.id)

    @staticmethod
    def _make_questions(
        themes: List[Theme],
        limit_questions: int = 10,
        limit_questions_in_theme: int = 2
    ) -> List[Question]:
        _questions = []

        for theme in themes:
            if len(theme.questions) > 0:
                for __ in range(0, limit_questions_in_theme, 1):
                    choice = random.choice(theme.questions)
                    _questions.append(choice)
                    theme.questions.remove(choice)
                    if len(theme.questions) <= 0:
                        break
        questions = []

        if len(_questions) < limit_questions:
            limit_questions = len(_questions)

        for __ in range(0, limit_questions, 1):
            choice = random.choice(_questions)
            questions.append(choice)
            _questions.remove(choice)

        return questions
