from copy import copy
from random import shuffle
from typing import Optional

import pandas as pd

import gensim.downloader as api


class BaseTaskGenerator:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.tasks = None
        self.task_template = {
            'raw': Optional[str],
            'object': Optional[str],
            'options': Optional[list],
            'answer': Optional[str],
            'type': Optional[str],
            'description': Optional[str],
        }
        self.task_methods = None
        # self.model = api.load("glove-wiki-gigaword-100") # TODO долгая загрузка, пока не работает

    def tasks_post_init(self):
        raise NotImplementedError

    def make_view_set(self, tasks_slice: pd.DataFrame) -> list:
        result = []
        for index, row in tasks_slice.iterrows():
            task = {
                'sentence': row['raw'],
                'options': [row['options']],
                'answers': [row['answer']],
                'result': [''],
                'total': 0,
            }
            result.append(task)
        return result

    def get_tasks(self, task_num: int = 20, task_types: list = None, seed: int = 0) -> list:
        if not task_types:
            tasks_slice_df = self.tasks.sample(n=task_num, random_state=seed)
        else:
            tasks_slice_df = self.tasks.query(f'description in {task_types}').sample(n=task_num, random_state=seed)

        task_view_set = self.make_view_set(tasks_slice_df)
        return task_view_set

    def get_tasks_types(self):
        tasks_types = self.tasks['description'].unique()
        return list(tasks_types)

    def compose_select_word_task_row(self,
                                     raw: str, token: str, answer: str, description: str, task_type: str, choices: list
                                     ) -> dict:
        task_row = copy(self.task_template)
        task_row['raw'] = raw
        task_row['object'] = str(token)
        task_row['options'] = choices
        task_row['answer'] = str(answer)
        task_row['description'] = description
        task_row['type'] = task_type
        return task_row

    def run_pipeline(self, is_shuffle: bool = True) -> pd.DataFrame:
        self.tasks = []

        if not self.task_methods:
            self.tasks_post_init()

        for index, row in self.df.iterrows():
            for method in self.task_methods:
                task_candidate = method(task_tokens=row['tokens'], raw_sentence=row['sentence'])
                if task_candidate:
                    self.tasks.extend(task_candidate)

        if is_shuffle:
            shuffle(self.tasks)

        self.tasks = pd.DataFrame(self.tasks)
        return self.tasks
