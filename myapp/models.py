from django.db import models
from uuid import uuid4


class Question(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    question_text = models.CharField(max_length=200)
    username = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True)  # Make choice nullable
    username = models.CharField(max_length=200)

    def __str__(self):
        return str(self.choice)




class Translation(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='translations')
    translated_question_text = models.CharField(max_length=200)
    translated_choices = models.CharField(max_length=1000)
    translated_correct_answer = models.UUIDField(default=uuid4, editable=False)
    language = models.CharField(max_length=50)

    def __str__(self):
        return self.translated_question_text
