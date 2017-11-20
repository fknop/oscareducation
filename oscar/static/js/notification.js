
$(document).ready(function(){

    $('[data-toggle="popover"]').popover();

    $('#bellicon').click(function() {
      $('#bellicon').css('color', '#787878')
    })

    socket = new WebSocket("ws://" + window.location.host + "/notification/");
    var notificationsContainer = $('<ul class="media-list"></ul>')

    const notifItemTemplate =
      `
      <a href="%redirect_url%" class="notif-item">
        <li class="media">
          <div class="media-left">
              <img class="media-object notif-list-item-icon" src="%icon_src%" alt="..."></img>
          </div>
          <div class="media-body">
            <div class="list-group-item-heading">%title%</div>
            <div class="notif-list-item-content" ><p>%content%</p></div>
            <div class="notif-list-item-footer"><p><span class="glyphicon glyphicon-time notif-item-footer-icon"></span>%date%</p></div>
          </div>
        </li>
      </a>
      `

    if (socket.readyState == WebSocket.OPEN) {
      socket.onopen();
    }

    socket.onmessage = function(e) {

      const newNotif = JSON.parse(e.data)
      let element;

      switch(newNotif.type) {
          case 'new_private_forum_thread':
            element = notifItemTemplate
                        .replace('%redirect_url%', '/forum/thread/' + newNotif.params.thread)
                        .replace('%icon_src%', '/static/img/icons/forum.png')
                        .replace('%title%', 'Forum: nouvelle discussion privée')
                        .replace('%content%', 'Ernest Biroute a créé une nouvelle discussion privée avec vous')
                        .replace('%date%', '24/03/1997')
          break
      }
      notificationsContainer.prepend(element)

      $('#bellicon').css('color', '#f58025')
      $('#bellicon').attr('data-content', $('<div></div>').append(notificationsContainer).html())

      if ($("#bellicon").next('div.popover:visible').length){ // if popover is open
        $('.popover-content ul.list-group').html($('<div></div>').append(notificationsContainer).html())
      }
    }
});
