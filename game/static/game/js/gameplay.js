$(document).ready(function() {
  var currentQuestion = null;
  var gameRoundId = null;
  var gameSessionId = null;
  var remainingRounds = 10;
  var timerInterval;
  var countdown;
  var questionNumber = 1; // Initialize question number

  $('#get-question-btn').click(function() {
    $(this).prop('disabled', true);
    getQuestion();
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
        .appendTo(choicesContainer)
        .click(function() {
          var selectedChoiceUuid = $(this).attr('data-choice-uuid');
          submitAnswer(selectedChoiceUuid);
        });
    });
  }

  function startTimer() {
    var countdownElement = $('#countdown');
    countdown = 10;

    countdownElement.text(countdown);

    timerInterval = setInterval(function() {
      countdown--;

      if (countdown <= 0) {
        clearInterval(timerInterval);
        submitAnswer(null);
        return;
      }

      countdownElement.text(countdown);
    }, 1000);
  }

  function submitAnswer(selectedChoiceUuid) {
  clearInterval(timerInterval);

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

      // Add the following code to handle the selected choice appearance
      var selectedChoiceButton = $('[data-choice-uuid="' + selectedChoiceUuid + '"]');
      selectedChoiceButton.prop('disabled', true);

      if (response.is_correct) {
        selectedChoiceButton.css({
          'background-color': 'green',
          'color': 'white'
        });
      } else {
        selectedChoiceButton.css({
          'background-color': 'red',
          'color': 'white'
        });
      }
    },
    error: function(xhr, status, error) {
      console.error('Error:', error);
    }
  });
}



  function redirectToResults() {
    if (gameSessionId) {
      window.location.href = '/results/' + gameSessionId + '/';
    }
  }
});
