from django.urls import path
from . import views
from myapp import views
app_name = 'game'

urlpatterns = [
    path('get_question/', views.get_question, name='get_question'),
    path('answer_question/', views.answer_question, name='answer_question'),
]
