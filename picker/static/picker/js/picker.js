function Picker () {
  this.rounds = {};
  this.championsUsed = [];
  this.clockInterval = null;

  this.getPortraitSource = function (champID) {
    return '/static/picker/images/champions/' + champID + '.png';
  };

  this.updateRounds = function (rounds) {
    for (let roundNum in rounds) {
      if (rounds[roundNum] != this.rounds[roundNum]) {
        let round = rounds[roundNum];
        let roundEle = $(".round[round-id='" + roundNum + "']");
        // If this is a new round.
        if (roundEle.length == 0) {
          let side = round.team;
          // Create the element.
          roundEle = $('<div></div>').addClass('round')
                                     .attr('round-id', roundNum);
          let portrait = $('<img></img>').addClass('portrait');
          roundEle.append(portrait);

          // Add it to the correct sidebar.
          if (side.toLowerCase() == 'r') {
            if (round.type.toLowerCase() == 'p') {
              $('.red.picks').append(roundEle);
              portrait.addClass('pick');
              roundEle.addClass('pick');
            } else {
              $('.red.bans').append(roundEle);
              portrait.addClass('ban');
              roundEle.addClass('ban');
            }
          } else {
            if (round.type.toLowerCase() == 'p') {
              $('.blue.picks').append(roundEle);
              portrait.addClass('pick');
              roundEle.addClass('pick');
            } else {
              $('.blue.bans').append(roundEle);
              portrait.addClass('ban');
              roundEle.addClass('ban');
            }
          }
        }

        // Add the image.
        if (round.championID) {
          roundEle.find('img.portrait').attr('src', this.getPortraitSource(round.championID));
        }
      }
    }
  };

  this.updateChampionSearch = function (picked) {
    for (let c of picked) {
      var ele = $(".champion[champion-id='" + c + "']");
      ele.remove();
    }
    this.championsUsed = picked;
  };


  this.updateClock = function (duration) {
    if (this.clockInterval) {
      clearInterval(this.clockInterval);
    }

    var secondsLeft = duration;
    var clockEle = $('#clock');
    console.log(secondsLeft);

    var clockInterval = setInterval(function() {
      if (secondsLeft <= 0) {
        clockEle.text(0);
        clearInterval(clockInterval);
      } else {
        clockEle.text(secondsLeft);
        secondsLeft -= 1
      }
    }, 1000);

    this.clockInterval = clockInterval;
  };

  /*
  this.updateClock = function (endTimestamp) {
    if (this.clockInterval) {
      clearInterval(this.clockInterval);
    }

    var now = Math.round(new Date().getTime() / 1000);
    var secondsLeft = endTimestamp - now;
    var clockEle = $('#clock');
    console.log(endTimestamp);
    console.log(now);
    console.log(secondsLeft);

    var clockInterval = setInterval(function() {

      if (secondsLeft <= 0) {
        clockEle.text(0);
        clearInterval(clockInterval);
      } else {
        clockEle.text(secondsLeft);
        secondsLeft -= 1
      }
    }, 1000);

    this.clockInterval = clockInterval;
  };
  */

  this.updateCurrentRound = function (currentRound) {
    $('.round').removeClass('current').removeClass('ondeck');
    $(".round[round-id='" + currentRound + "']").addClass('current');
    $(".round[round-id='" + (currentRound + 1) + "']").addClass('ondeck');
  }

  this.updateStartButton = function (started) {
    if (started) {
      $('#start-game').hide();
    }
  }

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
    this.updateClock(data.duration);
    this.updateCurrentRound(data.currentRound);
    this.updateStartButton(data.started);
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
      'type': 'pick',
    };

    socket.send(JSON.stringify(message));
  });

  $('#start-game').click(function(e) {
    $(this).hide();
    message = {
      'type': 'start',
    };
    socket.send(JSON.stringify(message));
  });
});
