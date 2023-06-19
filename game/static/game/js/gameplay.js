$(document).ready(function() {
  var currentQuestion = null;
  var gameRoundId = null;
  var gameSessionId = null;
  var remainingRounds = 10; var timerInterval;


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
    // Email validation regex pattern
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
            // Display game session ended message
            $('#question-container').hide();
            $('#results').text('Game session ended.');
            $('#results').show();

            redirectToResults();
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

            // Enable the "Submit Answer" button when a question is retrieved
            $('#submit-answer-btn').prop('disabled', false);
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
    var countdown = 10; // Change the value according to the time limit in seconds
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

          $('#get-question-btn').prop('disabled', false);

          redirectToResults();
        } else {
          getQuestion();
        }
      },
      error: function(xhr, status, error) {
        console.error('Error:', error);
      }
    });
  } else {
      getQuestion();
}}

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