from django.contrib import admin
from .models import Question, Answer, Choice, Player, GameRound, Results, GameSession


class ChoiceInline(admin.TabularInline):
    model = Choice
    fields = ['display_uuid', 'choice_text', 'is_correct']
    readonly_fields = ['display_uuid']
    extra = 1

    def display_uuid(self, obj):
        return str(obj.uuid)


class GameRoundInline(admin.StackedInline):
    model = GameRound



class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'get_player_name')
    inlines = [ChoiceInline]

    def get_player_name(self, obj):
        return obj.player.name if obj.player else None

    get_player_name.short_description = 'Player'


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('choice', 'get_player_name', 'get_question_text', 'get_game_round')

    def get_player_name(self, obj):
        return obj.player.name if obj.player else None

    def get_question_text(self, obj):
        return obj.question.question_text if obj.question else None

    def get_game_round(self, obj):
        return obj.game_round

    get_player_name.short_description = 'Player'
    get_question_text.short_description = 'Question'
    get_game_round.short_description = 'Game Round'


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')


class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('player', 'start_time', 'end_time')

    def start_time(self, obj):
        return obj.start_time.strftime('%Y-%m-%d %H:%M:%S') if obj.start_time else None

    def end_time(self, obj):
        return obj.end_time.strftime('%Y-%m-%d %H:%M:%S') if obj.end_time else None

    start_time.short_description = 'Start Time'
    end_time.short_description = 'End Time'


class GameRoundAdmin(admin.ModelAdmin):
    list_display = ('get_player_name', 'question_start_time', 'question_end_time')

    def get_player_name(self, obj):
        return obj.player.name if obj.player else None

    def question_start_time(self, obj):
        if obj.current_question and obj.question_start_time:
            return obj.question_start_time.strftime('%Y-%m-%d %H:%M:%S') if obj.question_start_time else None
        else:
            return None

    def question_end_time(self, obj):
        if obj.current_question and obj.question_end_time:
            return obj.question_end_time.strftime('%Y-%m-%d %H:%M:%S') if obj.question_end_time else None
        else:
            return None

    get_player_name.short_description = 'Player'
    question_start_time.short_description = 'Question Start Time'
    question_end_time.short_description = 'Question End Time'


class ResultsAdmin(admin.ModelAdmin):
    list_display = ('game_round', 'correct_answers', 'wrong_answers')

    def game_round(self, obj):
        return obj.game_round

    game_round.short_description = 'Game Round'


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Choice)
admin.site.register(Player, PlayerAdmin)
admin.site.register(GameRound, GameRoundAdmin)
admin.site.register(Results, ResultsAdmin)
admin.site.register(GameSession, GameSessionAdmin)
