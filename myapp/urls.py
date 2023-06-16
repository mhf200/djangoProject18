from django.urls import path

from . import views

urlpatterns = [
    path('get_question/', views.get_question, name='get_question'),
    path('answer_question/', views.answer_question, name='answer_question'),


]
