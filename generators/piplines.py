from copy import copy
from random import shuffle

import numpy as np

from generators.base import BaseTaskGenerator


class TaskGenerator(BaseTaskGenerator):

    def tasks_post_init(self):
        self.task_methods = [
            self.task_articles,
            self.task_verbs_forms,
            self.task_adj_degrees,
            # self.task_similar_sent
        ]

    @staticmethod
    def _mask_word(tokens_ls: list, position: int) -> str:
        raw_sent = copy(tokens_ls)
        raw_sent[position] = '_____'
        return ' '.join([str(x) for x in raw_sent])

    def task_articles(self, task_tokens: list, raw_sentence=None):
        description = 'Укажите правильный артикль'
        task_type = 'select_word'
        tasks_content = []
        choices = {'a', 'an', 'the'}
        for position, token in enumerate(task_tokens):

            if token.pos_ == 'DET':
                choices.add(str(token).lower())

                raw_sentence = self._mask_word(task_tokens, position)

                task = self.compose_select_word_task_row(
                    raw_sentence, token, token, description, task_type, list(choices)
                )

                tasks_content.append(task)

        if not tasks_content:
            return

        return tasks_content

    def task_verbs_forms(self, task_tokens: list, raw_sentence=None):
        description = 'Выберите правильную форму глагола'
        task_type = 'select_word'
        tasks_content = []

        for position, token in enumerate(task_tokens):

            if token.pos_ == 'VERB':
                choices = set()
                choices.add(str(token._.inflect('VBP')))
                choices.add(str(token._.inflect('VBZ')))
                choices.add(str(token._.inflect('VBG')))
                choices.add(str(token._.inflect('VBD')))
                choices.add(str(token))
                choices = list(choices)
                shuffle(choices)

                raw_sentence = self._mask_word(task_tokens, position)

                task = self.compose_select_word_task_row(raw_sentence, token, token, description, task_type, choices)

                tasks_content.append(task)

        if not tasks_content:
            return

        return tasks_content

    def task_adj_degrees(self, task_tokens: list, raw_sentence=None):
        description = 'Степень сравнения прилагательного'
        task_type = 'select_word'
        tasks_content = []

        for position, token in enumerate(task_tokens):

            if token.tag_ == 'JJS' or token.tag_ == 'JJR' or token.tag_ == 'JJ':
                choices = set()
                choices.add(str(token._.inflect('JJS')))
                choices.add(str(token._.inflect('JJR')))
                choices.add(str(token._.inflect('JJ')))
                choices.add(str(token))

                result = []
                for word in choices:
                    if word != 'None':
                        result.append(word)

                if len(result) < 2:
                    continue

                shuffle(result)

                raw_sentence = self._mask_word(task_tokens, position)

                task = self.compose_select_word_task_row(raw_sentence, token, token, description, task_type, result)

                tasks_content.append(task)

        if not tasks_content:
            return

        return tasks_content

    def task_similar_sent(self, task_tokens: list, raw_sentence: str):
        description = 'Выберите подходящее по смыслу предложение'
        task_type = 'select_sentence'
        tasks_content = []
        new_sent_1, new_sent_2 = raw_sentence, raw_sentence
        i = 5
        for position, token in enumerate(task_tokens):
            if token.pos_ in ['VERB', 'ADV'] and token.text.lower() != '©':
                m, n = np.random.randint(0, i, 2)

                new_word_1 = self.model.most_similar(token.text.lower(), topn=i)[m][0]
                new_word_2 = self.model.most_similar(positive=[token.text.lower(), 'bad'],
                                                     negative=['good'],
                                                     topn=i)[n][0]

                new_word_1 = new_word_1.title() if token.text.istitle() else new_word_1
                new_word_2 = new_word_2.title() if token.text.istitle() else new_word_2

                new_sent_1 = new_sent_1.replace(token.text, new_word_1)
                new_sent_2 = new_sent_2.replace(token.text, new_word_2)
                choices = []
                choices.append(str(raw_sentence))
                choices.append(str(new_sent_1))
                choices.append(str(new_sent_2))

                result = []
                for word in choices:
                    if word != 'None':
                        result.append(word)

                if len(result) < 2:
                    continue

                shuffle(choices)

                task = self.compose_select_word_task_row(
                    "Выберете подходящее по смыслу предложение", token, raw_sentence, description, task_type, result
                )

                tasks_content.append(task)

        if not tasks_content:
            return

        return tasks_content
