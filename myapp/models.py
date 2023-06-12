from django.db import models
from uuid import uuid4
from django.core.exceptions import ValidationError
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
    correct_answer_uuid = models.UUIDField(default=uuid4)

    def __str__(self):
        return self.question_text

    def save(self, *args, **kwargs):
        if not self.correct_answer_uuid:
            correct_choice = self.choices.filter(is_correct=True).first()
            if correct_choice:
                self.correct_answer_uuid = correct_choice.uuid
        super().save(*args, **kwargs)


class Choice(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

    @property
    def choice_uuid(self):
        return str(self.uuid)


class Translation(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='translations')
    translated_question_text = models.CharField(max_length=200)
    translated_choices = models.CharField(max_length=1000)
    translated_correct_answer = models.UUIDField(default=uuid4, editable=False)
    language = models.CharField(max_length=50)

    def __str__(self):
        return self.translated_question_text


class GameSession(models.Model):
    STATUS_CHOICES = [
        ('WON', 'Won'),
        ('LOST', 'Lost'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_sessions')
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True, default=None)
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default='Won')

    def __str__(self):
        return f"GameSession for {self.player}"

    def is_completed(self):
        return self.game_rounds.count() == 10

    def clean(self):
        super().clean()
        if self.game_rounds.count() > 10:
            raise ValidationError("A GameSession cannot have more than 10 GameRounds.")

    def calculate_status(self):
        correct_answers_count = self.game_rounds.first().results.correct_answers
        if correct_answers_count == 10:
            self.status = 'WON'
        else:
            self.status = 'LOST'

    def save(self, *args, **kwargs):
        if self.is_completed() and not self.end_time and not self.status:
            self.end_time = timezone.now()
            self.calculate_status()
        super().save(*args, **kwargs)


class GameRound(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_rounds')
    question_start_time = models.DateTimeField(null=True)
    question_end_time = models.DateTimeField(null=True, default=None)
    current_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    time_taken = models.IntegerField(null=True)
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='game_rounds', default=None,
                                     null=True)

    def __str__(self):
        return f"{self.player}'s GameRound"


class Answer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True, null=True)
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name='answers', null=True, default=None)

    def __str__(self):
        return f"Answer for {self.question} by {self.player}"


class Results(models.Model):
    game_round = models.OneToOneField(GameRound, on_delete=models.CASCADE, related_name='results')
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    total_answers = models.IntegerField(default=0)
    not_answered_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Results for {self.game_round}"
