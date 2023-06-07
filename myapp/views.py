from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, Answer, Translation, Choice, Player, GameRound, Results, GameSession
from translate import Translator
from django.utils import timezone

@csrf_exempt
def get_question(request):
    if request.method == 'GET':
        language = request.GET.get('language')

        player_name = request.GET.get('player_name')
        player_email = request.GET.get('player_email')

        if player_name and player_email:
            player, _ = Player.objects.get_or_create(name=player_name, email=player_email)

            game_session, created = GameSession.objects.get_or_create(player=player)
            if created:
                game_session.start_time = timezone.now()

            if game_session.is_completed():
                return JsonResponse({'message': 'GameSession completed.'})

            game_round, _ = GameRound.objects.get_or_create(player=player)
            game_round.current_question = None
            game_round.question_start_time = timezone.now()

            time_limit = 10
            game_round.question_end_time = game_round.question_start_time + timedelta(seconds=time_limit)

            game_round.save()

            # Add the game_round to the game_session
            game_session.game_rounds.add(game_round)

            # Add the game_session to the results
            results, _ = Results.objects.get_or_create(game_round=game_round)

        question = Question.objects.order_by('?').first()

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

        game_round.current_question = question
        game_round.save()

        response = {
            'question_uuid': str(question.uuid),
            'question_text': translation.translated_question_text,
            'answer_choices': translation.translated_choices.split(','),
            'choice_uuids': choice_uuids,
            'correct_answer': translated_correct_answer,
        }

        return JsonResponse(response)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


@csrf_exempt
def answer_question(request):
    if request.method == 'POST':
        question_uuid = request.POST.get('question_uuid')
        answer_text = request.POST.get('answer_text')

        if question_uuid and answer_text:
            try:
                question = Question.objects.get(uuid=question_uuid)
                selected_choice = Choice.objects.get(uuid=answer_text, question=question)

                player_name = request.POST.get('player_name')
                player_email = request.POST.get('player_email')

                if player_name and player_email:
                    player, _ = Player.objects.get_or_create(name=player_name, email=player_email)

                    game_round, _ = GameRound.objects.get_or_create(player=player)

                    if game_round.current_question != question:
                        return JsonResponse({'error': 'Invalid question.'}, status=400)

                    current_time = timezone.now()
                    if current_time > game_round.question_end_time:
                        return JsonResponse({'error': 'Time limit exceeded.'}, status=400)

                    time_taken = current_time - game_round.question_start_time

                    answer = Answer(player=player, question=question, choice=selected_choice, game_round=game_round)
                    answer.save()

                    if selected_choice.is_correct:
                        game_round.results.correct_answers += 1
                        game_round.results.save()
                        return JsonResponse({'status': 'success'})
                    else:
                        game_round.results.wrong_answers += 1
                        game_round.results.save()
                        return JsonResponse({'status': 'failure'})

                    # Update the current_question of the GameRound after answering
                    game_round.current_question = None
                    game_round.save()

            except (Question.DoesNotExist, Choice.DoesNotExist):
                return JsonResponse({'error': 'Invalid question or choice.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)
