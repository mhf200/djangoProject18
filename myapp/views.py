import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, Answer, Translation , Choice
from translate import Translator

@csrf_exempt
def get_question(request):
    if request.method == 'GET':
        language = request.GET.get('language')

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

            correct_choice = question.choices.filter(is_correct=True).first()  # Get the correct choice
            translated_correct_answer = str(correct_choice.uuid)  # Use the UUID of the correct choice

            translation = Translation(
                question=question,
                translated_question_text=translated_question,
                translated_choices=','.join(translated_choices),
                translated_correct_answer=translated_correct_answer,
                language=language
            )
            translation.save()

        else:
            choice_uuids = [str(choice.uuid) for choice in question.choices.all()]  # Populate choice_uuids here
            translated_correct_answer = str(question.choices.filter(is_correct=True).first().uuid)

        response = {
            'question_uuid': str(question.uuid),
            'question_text': translation.translated_question_text,
            'answer_choices': translation.translated_choices.split(','),
            'choice_uuids': choice_uuids,  # Pass the list of choice UUIDs
            'username': question.username,
            'correct_answer': translated_correct_answer
        }
        return JsonResponse(response)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


@csrf_exempt
def answer_question(request):
    choice_uuids = []  # Move this line here

    if request.method == 'POST':
        question_uuid = request.POST.get('question_uuid')
        username = request.POST.get('username')
        answer_text = request.POST.get('answer_text')

        if question_uuid and username and answer_text:
            try:
                question = Question.objects.get(uuid=question_uuid)

                # Retrieve the selected answer choice
                selected_choice = Choice.objects.get(uuid=answer_text, question=question)

                # Update the correct answer choice in the Answer model
                Answer.objects.update_or_create(
                    question=question,
                    username=username,
                    defaults={'choice': selected_choice}
                )

                # Retrieve the updated correct answer choice
                updated_correct_choice = question.choices.filter(is_correct=True).first()

                if selected_choice.uuid == updated_correct_choice.uuid:
                    return JsonResponse({'success': 'Answer is correct!'})
                else:
                    return JsonResponse({'error': 'Answer is incorrect.'}, status=400)

            except (Question.DoesNotExist, Choice.DoesNotExist):
                return JsonResponse({'error': 'Question or choice does not exist.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)
