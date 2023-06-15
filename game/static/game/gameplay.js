$(document).ready(function() {
  var currentQuestion = null;
  var gameRoundId = null;
  var gameSessionId = null;
  var remainingRounds = 10;

  $('#get-question-btn').click(function() {
    getQuestion();
  });

  $('#submit-answer-btn').click(function() {
    submitAnswer();
  });

  function getQuestion() {
    var playerName = $('#player-name').val();
    var playerEmail = $('#player-email').val();

    if (playerName && playerEmail) {
      $.ajax({
        type: 'GET',
        url: '/get_question/',
        data: {
          language: 'en',
          player_name: playerName,
          player_email: playerEmail
        },
        success: function(response) {
          if (response.message === 'Game session ended.') {
            // Display game session ended message
            $('#question-container').hide();
            $('#results').text('Game session ended.');
            $('#results').show();
          } else if (response.message === 'No more questions available.') {
            // Display no more questions available message
            $('#question-container').hide();
            $('#results').text('No more questions available. You have submitted 10 answers.');
            $('#results').show();
          } else {
            currentQuestion = response.question_uuid;
            gameRoundId = response.game_round_id;
            gameSessionId = response.game_session_id;

            $('#player-info').hide();
            $('#question-container').show();

            $('#question').text(response.question_text);
            displayChoices(response.choices);

            startTimer();
          }
        },
        error: function(xhr, status, error) {
          console.error('Error:', error);
        }
      });
    } else {
      alert('Please enter your name and email.');
    }
  }

  function displayChoices(choices) {
    var choicesContainer = $('#choices');
    choicesContainer.empty();

    choices.forEach(function(choice) {
      var choiceButton = $('<button></button>')
        .text(choice.choice_text)
        .attr('data-choice-uuid', choice.uuid)
        .appendTo(choicesContainer);
    });
  }

  function startTimer() {
    var countdownElement = $('#countdown');
    var countdown = 10;
    countdownElement.text(countdown);

    var timerInterval = setInterval(function() {
      countdown--;

      if (countdown <= 0) {
        clearInterval(timerInterval);

      }

      countdownElement.text(countdown);
    }, 1000);
  }

  function submitAnswer() {
  var selectedChoiceUuid = $('#choices button.selected').attr('data-choice-uuid');

  if (selectedChoiceUuid) {
    $.ajax({
      type: 'POST',
      url: '/answer_question/',
      data: {
        question_uuid: currentQuestion,
        selected_choice_uuid: selectedChoiceUuid,
        game_round_id: gameRoundId,
        game_session_id: gameSessionId

      },
      success: function(response) {

        remainingRounds--;

        if (response.message === 'Game session ended.') {

          $('#question-container').hide();
          $('#results').text('Game session ended! You have submitted 10 answers.');

          $('#results').show();

        } else {
          getQuestion();
        }
      },
      error: function(xhr, status, error) {
        console.error('Error:', error);
      }
    });
  } else {
    alert('Please select an answer.');
  }
}

  $('#choices').on('click', 'button', function() {
    $('#choices button').removeClass('selected');
    $(this).addClass('selected');
  });
});


