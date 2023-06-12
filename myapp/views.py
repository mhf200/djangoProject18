from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, Answer, Translation, Choice, Player, GameRound, Results, GameSession
from translate import Translator
from django.utils import timezone
import datetime
from uuid import UUID


import random

@csrf_exempt
def get_question(request):
    if request.method == 'GET':
        language = request.GET.get('language')
        player_name = request.GET.get('player_name')
        player_email = request.GET.get('player_email')

        if player_name and player_email:
            player, _ = Player.objects.get_or_create(name=player_name, email=player_email)

            game_sessions = GameSession.objects.filter(player=player).order_by('-start_time')

            if game_sessions.exists():
                latest_game_session = game_sessions.first()

                # Check if the latest game session is completed
                if latest_game_session.is_completed():
                    game_session = GameSession(player=player, start_time=timezone.now())
                    game_session.save()
                    return JsonResponse({'message': 'GameSession ended.'})

                # Set the end time of the latest game session if it's not already set
                if latest_game_session.end_time is None:
                    latest_game_session.end_time = timezone.now()
                    latest_game_session.save()

                game_session = latest_game_session
            else:
                game_session = GameSession(player=player, start_time=timezone.now())
                game_session.save()

            previous_question_uuids = Answer.objects.filter(player=player).values_list('question__uuid', flat=True)

            # Exclude previously answered questions
            questions = Question.objects.exclude(uuid__in=previous_question_uuids)

            if questions.exists():
                # Select a random question from the remaining available questions
                question = questions.order_by('?').first()

                translation = Translation.objects.filter(question=question, language=language).first()

                if not translation:
                    translator = Translator(to_lang=language)
                    translated_question = translator.translate(question.question_text)
                    translated_choices = [translator.translate(choice.choice_text) for choice in question.choices.all()]
                    choices = list(question.choices.values('uuid', 'choice_text'))
                    correct_choice = question.choices.filter(is_correct=True).first()
                    translated_choices = [choice.choice_text for choice in question.choices.all()]

                    translated_correct_answer = str(correct_choice.uuid) if correct_choice else ''

                    translation = Translation(
                        question=question,
                        translated_question_text=translated_question,
                        translated_choices=','.join(translated_choices),
                        translated_correct_answer=translated_correct_answer,
                        language=language
                    )
                    translation.save()

                else:
                    choices = list(question.choices.values('uuid', 'choice_text'))

                    translated_choices = translation.translated_choices.split(',')
                    translated_correct_answer = translation.translated_correct_answer

                # Check if the current game round is completed
                current_game_round = game_session.game_rounds.last()

                if current_game_round and current_game_round.question_end_time is None:
                    current_game_round.question_end_time = timezone.now()
                    current_game_round.save()

                # Create a new game round if the current one is completed or there is no current round
                if not current_game_round or current_game_round.question_end_time is not None:
                    game_round = GameRound(player=player, question_start_time=timezone.now())
                    game_round.save()
                    game_session.game_rounds.add(game_round)

                # Add the game_session to the results
                results, _ = Results.objects.get_or_create(game_round=game_round)

                # Update the current_question of the GameRound
                game_round.current_question = question
                game_round.save()

                response = {
                    'question_uuid': str(question.uuid),
                    'question_text': translation.translated_question_text,
                    'choices': choices,
                    'correct_answer_uuid': translated_correct_answer,
                    'game_round_id': game_round.id,
                    'game_session_id': game_session.id,
                }

                return JsonResponse(response)

            else:
                return JsonResponse({'message': 'No more questions available.'})

        else:
            return JsonResponse({'message': 'Invalid player information.'})

    else:
        return JsonResponse({'message': 'Invalid request method.'})






@csrf_exempt
def answer_question(request):
    if request.method == 'POST':
        question_uuid = request.POST.get('question_uuid')
        selected_choice_uuid = request.POST.get('selected_choice_uuid')
        game_round_id = request.POST.get('game_round_id')
        game_session_id = request.POST.get('game_session_id')

        if not question_uuid or not selected_choice_uuid or not game_round_id or not game_session_id:
            return JsonResponse({'message': 'Invalid request parameters.'})

        try:
            question = Question.objects.get(uuid=question_uuid)
            selected_choice = Choice.objects.get(uuid=selected_choice_uuid)
            game_round = GameRound.objects.get(id=game_round_id)
            game_session = GameSession.objects.get(id=game_session_id)

            if game_round.current_question != question or game_round.player != game_session.player:
                return JsonResponse({'message': 'Invalid question or game round.'}, status=400)

            # Check if the player's time for the question has exceeded the limit
            if game_round.question_start_time and game_round.question_end_time is None:
                elapsed_time = timezone.now() - game_round.question_start_time
                time_limit = 10
                if elapsed_time.total_seconds() > time_limit:
                    game_round.results.not_answered_count += 1
                    game_round.results.save()

                    # Set question_end_time to mark the question as expired
                    game_round.question_end_time = timezone.now()
                    game_round.save()
                    return JsonResponse({'error': 'Time limit exceeded.'}, status=400)

            # Check if the selected choice matches the correct answer
            is_correct = selected_choice.is_correct

            # Check if the selected choice belongs to the current question
            if selected_choice.question != question:
                is_correct = False

            answer = Answer(player=game_round.player, question=question, selected_choice=selected_choice,
                            is_correct=is_correct)
            answer.save()

            game_round.results.total_answers += 1

            if is_correct:
                game_round.results.correct_answers += 1
            else:
                game_round.results.wrong_answers += 1

            game_round.results.save()

            # Calculate and update the time_taken field in GameRound
            if game_round.question_start_time:
                elapsed_time = timezone.now() - game_round.question_start_time
                game_round.time_taken = elapsed_time.total_seconds()
                game_round.save()

            if is_correct:
                return JsonResponse({'message': 'Answer submitted successfully.'})
            else:
                # Clear the current question and game round if the answer is incorrect
                game_round.current_question = None
                game_round.save()
                return JsonResponse({'message': 'Invalid answer.'}, status=400)

        except (Question.DoesNotExist, Choice.DoesNotExist, GameRound.DoesNotExist, GameSession.DoesNotExist):
            return JsonResponse({'message': 'Invalid question or game round.'}, status=400)

    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=400)
