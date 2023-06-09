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
    game_round = models.ForeignKey('GameRound', on_delete=models.CASCADE, related_name='answers', default=None, null=True)

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

class Time(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='time')
    seconds = models.IntegerField(default=10)

    def __str__(self):
        return f"Time for {self.question}"

class GameRound(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_rounds')
    question_start_time = models.DateTimeField(null=True)
    question_end_time = models.DateTimeField(null=True, default=None)
    current_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.player}'s GameRound"



class Results(models.Model):
    game_round = models.OneToOneField(GameRound, on_delete=models.CASCADE, related_name='results')
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)

    def __str__(self):
        return f"Results for {self.game_round}"

class GameSession(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_sessions')
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True, default=None)
    game_rounds = models.ManyToManyField(GameRound, related_name='game_sessions')

    def __str__(self):
        return f"GameSession for {self.player}"

    def is_completed(self):
        return self.game_rounds.count() == 10