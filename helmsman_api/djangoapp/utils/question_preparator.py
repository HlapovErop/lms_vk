import random


class QuestionPreparator:
    @staticmethod
    def prepare_question(test):
        method = getattr(QuestionPreparator, test.type.format)
        if method is not None:
            test.template_data = method(test.template_data)
            return test
        else:
            raise AttributeError

    @staticmethod
    def true_false(data):
        data['answer'] = False
        return data

    @staticmethod
    def options(data):
        data['correct_answers'] = []
        return data

    @staticmethod
    def ratio(data):
        data['left'].update((key, 0) for key in data['left'])
        return data

    @staticmethod
    def matching(data):
        random.shuffle(data['left'])
        return data
