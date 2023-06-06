from django.contrib import admin
from .models import Question, Answer, Choice, Player, Gameplay


class ChoiceInline(admin.TabularInline):
    model = Choice
    fields = ['display_uuid', 'choice_text', 'is_correct']
    readonly_fields = ['display_uuid']
    extra = 1

    def display_uuid(self, obj):
        return str(obj.uuid)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'get_player_name')
    inlines = [ChoiceInline]

    def get_player_name(self, obj):
        return obj.player.name if obj.player else None

    get_player_name.short_description = 'Player'


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('choice', 'get_player_name', 'get_question_text', 'get_gameplay')

    def get_player_name(self, obj):
        return obj.player.name if obj.player else None

    def get_question_text(self, obj):
        return obj.question.question_text if obj.question else None

    def get_gameplay(self, obj):
        return obj.gameplay

    get_player_name.short_description = 'Player'
    get_question_text.short_description = 'Question'
    get_gameplay.short_description = 'Gameplay'


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')


class GameplayAdmin(admin.ModelAdmin):
    list_display = ('get_player_name', 'start_time_display', 'end_time_display')

    def get_player_name(self, obj):
        return obj.player.name if obj.player else None

    def start_time_display(self, obj):
        return obj.start_time.strftime('%Y-%m-%d %H:%M:%S')

    def end_time_display(self, obj):
        if obj.end_time:
            return obj.end_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None

    get_player_name.short_description = 'Player'
    start_time_display.short_description = 'Start Time'
    end_time_display.short_description = 'End Time'


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)  # Register the Answer model
admin.site.register(Player, PlayerAdmin)
admin.site.register(Gameplay, GameplayAdmin)
