from django.db import models
from uuid import uuid4
from django.utils import timezone

class Player(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Question(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    question_text = models.CharField(max_length=200)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='questions', null=True)

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
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='answers', null=True)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    gameplay = models.ForeignKey('Gameplay', on_delete=models.CASCADE, related_name='answers', default=None, null=True)

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

class Gameplay(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='gameplays')
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    question_start_time = models.DateTimeField(null=True)
    question_end_time = models.DateTimeField(null=True, default=None)
    current_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.player}'s Gameplay"

class Time(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='time')
    seconds = models.IntegerField(default=10)

    def __str__(self):
        return f"Time for {self.question}"
