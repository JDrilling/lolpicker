$(function() {

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
    var selectedID = $('.highlight').attr('id');

    $.ajax({
      url: "",
      data: {
        id: selectedID
      },
      type: "POST",
      dataType: "json",
    })
    .done(function(resp) {
      alert("Success: " + resp.success);
    })
    .fail(function(request, status, errorThrown) {
      alert("Error: " + JSON.parse(request.responseText).error);
    });
  });
});
