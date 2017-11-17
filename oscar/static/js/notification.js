
socket = new WebSocket("ws://" + window.location.host + "/notification/");

socket.onmessage = function(e) {
    alert(e.data);
}

if (socket.readyState == WebSocket.OPEN)
  socket.onopen();
