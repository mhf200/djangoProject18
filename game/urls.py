from django.urls import path
from myapp.views import get_question, answer_question
from game.views import results , gameplay , final_results



urlpatterns = [
    path('get_question/', get_question, name='get_question'),
    path('answer_question/', answer_question, name='answer_question'),
    path('results/<int:game_session_id>/', results, name='results'),
    path('gameplay/', gameplay, name='gameplay'),
    path('final_results/<int:game_session_id>/', final_results, name='final_results'),




]
