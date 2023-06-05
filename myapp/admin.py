from django.contrib import admin
from .models import Question, Answer, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    fields = ['display_uuid', 'choice_text', 'is_correct']
    readonly_fields = ['display_uuid']
    extra = 1

    def display_uuid(self, obj):
        return str(obj.uuid)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'username')
    inlines = [ChoiceInline]


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('choice', 'username', 'question')


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
