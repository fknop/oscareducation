
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
      const date = newNotif.created_date.day + '/'
                  + newNotif.created_date.month + '/' + newNotif.created_date.year
                  + " " + newNotif.created_date.hour + 'h'
                  + newNotif.created_date.minute
      let redirect_url, icon_src, title, content

      switch(newNotif.type) {
        
          case 'new_private_forum_thread':

            redirect_url = '/forum/thread/' + newNotif.params.thread_id
            icon_src = '/static/img/icons/forum.png'
            title = 'Forum: nouvelle discussion privée'
            content = newNotif.params.author.first_name + ' '
              + newNotif.params.author.last_name + ' a créé une nouvelle discussion privée avec vous'
          break

          case 'new_public_forum_thread':
          case 'new_class_forum_thread':

            redirect_url = '/forum/thread/' + newNotif.params.thread_id
            icon_src = '/static/img/icons/forum.png'
            title = 'Forum: nouvelle discussion de classe'
            content = newNotif.params.author.first_name + ' '
              + newNotif.params.author.last_name
              + ' a créé une nouvelle discussion dans votre classe: '
              + (newNotif.type == 'new_class_forum_thread' ?
                newNotif.params.class.name :
                newNotif.params.classes.filter(
                  c => c.id == newNotif.server_group.split('-').pop())[0])
          break
      }

      element = $(notifItemTemplate
                  .replace('%redirect_url%', redirect_url)
                  .replace('%icon_src%', icon_src)
                  .replace('%title%', title)
                  .replace('%content%', content)
                  .replace('%date%', date))

      notificationsContainer.prepend(element)

      $('#bellicon').css('color', '#f58025')
      $('#bellicon').attr('data-content', $('<div></div>').append(notificationsContainer).html())

      if ($('div.popover.fade.bottom.in').length){ // if popover is open
        $('.popover-content').html($('<div></div>').append(notificationsContainer).html())
      }
    }
});
