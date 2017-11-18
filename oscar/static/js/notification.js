
$(document).ready(function(){


  socket = new WebSocket("ws://" + window.location.host + "/notification/");

  var notificationsContainer = $('<ul class="list-group"></ul>')

var i =0

  socket.onmessage = function(e) {

    notificationsContainer.prepend('<li class="list-group-item">notif ' + i++ +'</li>')

    $('#bellicon').css('color', '#f58025')
    $('#bellicon').attr('data-content', $('<div></div>').append(notificationsContainer).html())
    $('[data-toggle="popover"]').popover();
  }

  if (socket.readyState == WebSocket.OPEN) {
    socket.onopen();
  }
    $('[data-toggle="popover"]').popover();

    $('#bellicon').click(function() {
      $('#bellicon').css('color', '#787878')
    })

});
