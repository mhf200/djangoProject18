from datetime import datetime, timedelta
import pytz
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, Answer, Translation, Choice, Player, Gameplay
from translate import Translator
from django.utils import timezone

@csrf_exempt
def get_question(request):
    if request.method == 'GET':
        language = request.GET.get('language')
        time_limit = int(request.GET.get('time_limit', 10))  # Default time limit is 10 seconds

        player_name = request.GET.get('player_name')
        player_email = request.GET.get('player_email')

        if player_name and player_email:
            player, _ = Player.objects.get_or_create(name=player_name, email=player_email)

            # Create or update the Gameplay object for the player
            gameplay, _ = Gameplay.objects.get_or_create(player=player)
            gameplay.current_question = None  # Reset the current question

            # Set the start time and end time for the question
            gameplay.question_start_time = timezone.now()
            gameplay.question_end_time = gameplay.question_start_time + timedelta(seconds=time_limit)

            # Save the gameplay object
            gameplay.save()

        question = Question.objects.order_by('?').first()

        translation = Translation.objects.filter(question=question, language=language).first()

        if not translation:
            # Translate the question and choices
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

        gameplay.current_question = question
        gameplay.save()

        response = {
            'question_uuid': str(question.uuid),
            'question_text': translation.translated_question_text,
            'answer_choices': translation.translated_choices.split(','),
            'choice_uuids': choice_uuids,
            'correct_answer': translated_correct_answer
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

                    gameplay, _ = Gameplay.objects.get_or_create(player=player)

                    if gameplay.current_question != question:
                        return JsonResponse({'error': 'Invalid question.'}, status=400)

                    current_time = timezone.now()
                    if current_time > gameplay.question_end_time:
                        return JsonResponse({'error': 'Time limit exceeded.'}, status=400)

                    time_taken = current_time - gameplay.question_start_time

                    answer = Answer(player=player, question=question, choice=selected_choice, gameplay=gameplay)
                    answer.save()

                    if selected_choice.is_correct:
                        gameplay.correct_answers += 1
                        gameplay.save()
                        return JsonResponse({'status': 'success'})
                    else:
                        gameplay.wrong_answers += 1
                        gameplay.save()
                        return JsonResponse({'status': 'failure'})

            except (Question.DoesNotExist, Choice.DoesNotExist):
                return JsonResponse({'error': 'Invalid question or choice.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def gameplay_results(request, player_id):
    try:
        player = Player.objects.get(id=player_id)
        gameplay = Gameplay.objects.get(player=player)
        answered_questions = Answer.objects.filter(player=player, gameplay=gameplay).values_list('question', flat=True).distinct()

        questions = Question.objects.filter(id__in=answered_questions)

        context = {
            'player_name': player.name,
            'player_email': player.email,
            'correct_answers': gameplay.correct_answers,
            'wrong_answers': gameplay.wrong_answers,
            'answered_questions': questions
        }

        return render(request, 'results.html', context)
    except (Player.DoesNotExist, Gameplay.DoesNotExist):
        return HttpResponse('Player or Gameplay does not exist.')

