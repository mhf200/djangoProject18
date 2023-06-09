from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, Answer, Translation, Choice, Player, GameRound, Results, GameSession
from translate import Translator
from django.utils import timezone
from uuid import UUID


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
                else:
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
                    translated_choices = []
                    choice_uuids = []

                    for choice in question.choices.all():
                        translated_choice = translator.translate(choice.choice_text)
                        translated_choices.append(translated_choice)
                        choice_uuids.append(str(choice.uuid))

                    correct_choice = question.choices.filter(is_correct=True).first()
                    translated_correct_answer = str(correct_choice.uuid)

                    translation = Translation(
                        question=question,
                        translated_question_text=translated_question,
                        translated_choices=','.join(translated_choices),
                        translated_correct_answer=translated_correct_answer,
                        language=language
                    )
                    translation.save()

                else:
                    choice_uuids = [str(choice.uuid) for choice in question.choices.all()]
                    translated_correct_answer = str(question.choices.filter(is_correct=True).first().uuid)

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
                    'choices': translation.translated_choices.split(','),
                    'correct_answer_uuid': translation.translated_correct_answer,
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
        answer_text = request.POST.get('answer_text')
        player_name = request.POST.get('player_name')
        player_email = request.POST.get('player_email')

        if question_uuid and answer_text and player_name and player_email:
            try:
                player, _ = Player.objects.get_or_create(name=player_name, email=player_email)
                question = Question.objects.get(uuid=question_uuid)
                selected_choice = Choice.objects.get(uuid=UUID(answer_text), question=question)

                game_round = GameRound.objects.filter(player=player, current_question=question).first()

                if game_round:
                    answer = Answer(player=player, question=question, choice=selected_choice, game_round=game_round)
                    answer.save()

                    if selected_choice.is_correct:
                        game_round.results.correct_answers += 1
                        game_round.results.save()
                        is_correct = True
                    else:
                        game_round.results.wrong_answers += 1
                        game_round.results.save()
                        is_correct = False

                    # Generate Results for the GameRound
                    results, created = Results.objects.get_or_create(game_round=game_round)
                    if created:
                        results.player = player
                    results.answer = answer
                    results.is_correct = is_correct
                    results.save()

                    # Set question_end_time when the player answers their game round question
                    game_round.question_end_time = timezone.now()
                    game_round.save()

                    # Update the current_question of the GameRound only if the answer is wrong
                    if not is_correct:
                        game_round.current_question = None
                        game_round.save()

                    return JsonResponse({'status': 'success'})

                else:
                    return JsonResponse({'error': 'Invalid game round.'}, status=400)

            except Question.DoesNotExist:
                return JsonResponse({'error': 'Invalid question.'}, status=400)

            except Choice.DoesNotExist:
                return JsonResponse({'error': 'Invalid choice.'}, status=400)

            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid answer format.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)