$(document).ready(function() {
  var currentQuestion = null;
  var gameRoundId = null;
  var gameSessionId = null;
  var remainingRounds = 10;
  var timerInterval;

  var questionNumber = 1; // Initialize question number

  $('#get-question-btn').click(function() {
    $(this).prop('disabled', true);
    getQuestion();
  });

  $('#submit-answer-btn').click(function() {
    submitAnswer();
  });

  function getQuestion() {
    var playerName = $('#player-name').val();
    var playerEmail = $('#player-email').val();

    if (playerName && playerEmail) {
      var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (emailPattern.test(playerEmail)) {
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
              $('#question-container').hide();
              $('#results').text('Game session ended.');
              $('#results').show();
              redirectToResults();
            } else if (response.message === 'No more questions available.') {
              $('#question-container').hide();
              $('#results').text('No more questions available.');
              $('#results').show();
            } else {
              currentQuestion = response.question_uuid;
              gameRoundId = response.game_round_id;
              gameSessionId = response.game_session_id;

              $('#player-info').hide();
              $('#question-container').show();

              $('#question').text('Question ' + questionNumber + ': ' + response.question_text);
              displayChoices(response.choices);
              startTimer();

              $('#submit-answer-btn').unbind('click');
              $('#submit-answer-btn').click(function() {
                submitAnswer();
              });
            }
          },
          error: function(xhr, status, error) {
            console.error('Error:', error);
          }
        });
      } else {
        alert('Please enter a valid email address.');
      }
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

    timerInterval = setInterval(function() {
      countdown--;

      if (countdown <= 0) {
        clearInterval(timerInterval);
        submitAnswer();
        return;
      }

      countdownElement.text(countdown);
    }, 1000);
  }

  function submitAnswer() {
    clearInterval(timerInterval);
    var selectedChoiceUuid = $('#choices button.selected').attr('data-choice-uuid');

    if (selectedChoiceUuid || countdown <= 0) {
      if (!selectedChoiceUuid) {
        selectedChoiceUuid = null;
      }

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

          if (remainingRounds <= 0 || response.message === 'Game session ended.') {
            $('#question-container').hide();
            $('#results').text('Game session ended! You have submitted 10 answers.');
            $('#results').show();
            redirectToResults();
          } else {
            questionNumber++; // Increment question number
            getQuestion(); // Next Question
          }
        },
        error: function(xhr, status, error) {
          console.error('Error:', error);
        }
      });
    } else {
      getQuestion();
    }
  }

  $('#choices').on('click', 'button', function() {
    $('#choices button').removeClass('selected');
    $(this).addClass('selected');
  });

  function restartGame() {
    window.location.href = '/gameplay/';
  }

  $('#restart-btn').click(function() {
    restartGame();
  });

  function redirectToResults() {
    if (gameSessionId) {
      window.location.href = '/results/' + gameSessionId + '/';
    }
  }
});
