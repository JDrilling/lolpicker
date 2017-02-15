function Picker () {
  this.rounds = {};
  this.championsUsed = [];
  this.clockInterval = null;

  this.updateRounds = function (rounds) {
    for (let roundNum in rounds) {
      if (rounds[roundNum] != this.rounds[roundNum]) {
        let round = rounds[roundNum];
        let roundEle = $(".round[round-id='" + roundNum + "']");
        // If this is a new round.
        if (roundEle.length == 0) {
          var side = round.team;
          // Create the element.
          roundEle = $('<div></div>').addClass('round')
                                     .attr('round-id', roundNum)
                                     .append($('<img></img>').addClass('portrait'));

          // Add it to the correct sidebar.
          if (side.toLowerCase() == 'r') {
            if (round.type.toLowerCase() == 'p') {
              $('#red-side .picks').append(roundEle);
            } else {
              $('#red-side .bans').append(roundEle);
            }
          } else {
            if (round.type.toLowerCase() == 'p') {
              $('#blue-side .picks').append(roundEle);
            } else {
              $('#blue-side .bans').append(roundEle);
            }
          }
        }

        // Add the image.
        if (round.championID) {
          var championHTML = $("[champion-id='" + round.championID + "']");
          roundEle.find('img').attr('src', championHTML.find('img').attr('src'));
        }
      }
    }
  };

  this.updateChampionSearch = function (picked) {
    for (let c of picked) {
      var ele = $(".champion[champion-id='" + c + "']");
      ele.hide();
    }
    this.championsUsed = picked;
  };

  this.updateClock = function (endTimestamp) {
    if (this.clockInterval) {
      clearInterval(this.clockInterval);
    }

    var clockInterval = setInterval(function() {
      var now = new Date().getTime();
      var secondsLeft = Math.floor((endTimestamp - now) / (1000));
      var clockEle = $('#clock');

      if (secondsLeft <= 0) {
        clockEle.text(0);
        clearInterval(clockInterval);
      }

      clockEle.text(secondsLeft);
    }, 1000);

    this.clockInterval = clockInterval;
  };

  this.updateUI = function (data) {
    rounds = data.rounds;
    used = [];
    for (roundNumber in rounds) {
      let round = rounds[roundNumber];
      if (round.championID !== null) {
        used.push(round.championID);
      }
    }

    this.updateRounds(rounds);
    this.updateChampionSearch(used);
    this.updateClock(new Date().getTime() + 3 * 1000);
  };
}

$(function() {
  var picker = new Picker();

  var socket = new WebSocket("ws://" + window.location.host + window.location.pathname);
  socket.onmessage = function(message) {
    messageJson = JSON.parse(message.data);
    if (!messageJson.success) {
      alert(messageJson.error);
    } else {
      console.log(JSON.stringify(messageJson.data));
      picker.updateUI(messageJson.data);
    }
  }


  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    }
  });


  var $champions = $('.champion').click(function(e) {
    e.preventDefault();
    $champions.removeClass('highlight');
    $(this).addClass('highlight');
  });


  $('#champion-confirm').click(function(e) {
    var selectedID = $('.champion.highlight').attr('champion-id');
    message = {
      'pick': selectedID,
    };

    socket.send(JSON.stringify(message));

  });
});
