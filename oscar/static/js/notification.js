
$(document).ready(function(){

    initPageAndSocket()
    socket.onmessage = onMessageSocketHandler

    function initPageAndSocket() {

        $('[data-toggle="popover"]').popover();

        $('#bellicon').click(function() {
          $('#bellicon').css('color', '#787878')
        })

        socket = new WebSocket("ws://" + window.location.host + "/notification/");

        if (socket.readyState == WebSocket.OPEN) {
          socket.onopen();
        }
    }

    function onMessageSocketHandler(e) {

        const newNotif = JSON.parse(e.data)
        let skip = currentUser.id == newNotif.params.author.id))

        if (!skip)
          updateDOM(newNotif)
    }

    function updateDOM(newNotif) {

        const notificationsContainer = $('<ul class="media-list"></ul>')
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
          const templateParams = getTemplateParams(newNotif)

          element = $(notifItemTemplate
                      .replace('%redirect_url%', templateParams.redirect_url)
                      .replace('%icon_src%', templateParams.icon_src)
                      .replace('%title%', templateParams.title)
                      .replace('%content%', templateParams.content)
                      .replace('%date%', templateParams.date))

          notificationsContainer.prepend(element)

          $('#bellicon').css('color', '#f58025')
          $('#bellicon').attr('data-content', $('<div></div>').append(notificationsContainer).html())

          if ($('div.popover.fade.bottom.in').length){ // if popover is open
            $('.popover-content').html($('<div></div>').append(notificationsContainer).html())
          }
    }

    function getTemplateParams(newNotif) {

        const templateParams = {}

        templateParams.date = newNotif.created_date.day + '/'
                    + newNotif.created_date.month + '/' + newNotif.created_date.year
                    + " " + newNotif.created_date.hour + 'h'
                    + newNotif.created_date.minute

        switch(newNotif.type) {

            case 'new_private_forum_thread':
                addNewPvtForumThreadTempParams(templateParams, newNotif)
            break

            case 'new_public_forum_thread':
            case 'new_class_forum_thread':
                addNewClassTempParams(templateParams, newNotif)
            break

            case 'new_private_forum_message':
            case 'new_public_forum_message':
            case 'new_class_forum_message':
                addNewMsgTempParams(templateParams, newNotif)
            break
          }

          return templateParams;
    }

    function addNewPvtForumThreadTempParams(templateParams, newNotif) {

        templateParams.redirect_url = '/forum/thread/' + newNotif.params.thread_id
        templateParams.icon_src = '/static/img/icons/forum.png'
        templateParams.title = 'Forum: nouvelle discussion privée'
        templateParams.content = newNotif.params.author.first_name + ' '
          + newNotif.params.author.last_name + ' a créé une nouvelle discussion privée: '
          +  '<span class="notif-item-emph">' + newNotif.params.thread_title + '</span>'
    }

    function addNewClassTempParams(templateParams, newNotif) {

        templateParams.redirect_url = '/forum/thread/' + newNotif.params.thread_id
        templateParams.icon_src = '/static/img/icons/forum.png'
        templateParams.title = 'Forum: nouvelle discussion de classe'
        templateParams.content = newNotif.params.author.first_name + ' '
          + newNotif.params.author.last_name
          + ' a créé une nouvelle discussion dans votre classe: '
          + (newNotif.type == 'new_class_forum_thread' ?
            newNotif.params.class.name :
            newNotif.params.classes.filter(
              c => c.id == newNotif.server_group.split('-').pop())[0])
    }

    function addNewMsgTempParams(templateParams, newNotif) {

        templateParams.redirect_url = '/forum/thread/'
          + newNotif.params.thread_id + '/' + '#message-' + newNotif.params.msg_id
        templateParams.icon_src = '/static/img/icons/forum.png'
        templateParams.title = 'Forum: nouveau message'
        templateParams.content = newNotif.params.author.first_name + ' '
          + newNotif.params.author.last_name
          + ' a publié un nouveau message dans la discussion: '
          + '<span class="notif-item-emph">' + newNotif.params.thread_title + '</span>'
    }
    
});
