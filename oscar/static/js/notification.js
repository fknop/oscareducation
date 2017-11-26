
$(document).ready(function(){

    let receivedNotifications = []

    initPageAndSocket()
    socket.onmessage = onMessageSocketHandler

    function initPageAndSocket() {

        $('[data-toggle="popover"]').popover();

        fetchNotifs()

        $('#bellicon').click(function() {

            setUnreadNotifAsRead()
            $('#bellicon').css('color', '#787878')
        })

        socket = new WebSocket("ws://" + window.location.host + "/notification/");

        if (socket.readyState == WebSocket.OPEN) {
          socket.onopen();
        }
    }

    function fetchNotifs() {

        $.get("/notification/last/?medium=ws", function(data, status){

            const filteredNotifs = data.notifs.filter(function(n) {
                return (currentUser.id != n.params.author.id)
            })

            filteredNotifs.forEach(function(n) {
                receivedNotifications.push(n)
            })

            updateDOMForNotifications(filteredNotifs)
        });
    }

    function setUnreadNotifAsRead() {

        const unreadNotifs = receivedNotifications.filter(function(notif) {

            const read = (notif.seen.indexOf('' + currentUser.id) < 0)

            notif.seen += ' ' + currentUser.id

            return read

        }).map(function(notif) { return '' + notif.notif_id })

        if (unreadNotifs.length != 0) {

            $.ajax({
                type: 'POST',
                url: '/notification/seen/',
                data: JSON.stringify({ notif_ids: unreadNotifs })
            });
        }
    }

    function onMessageSocketHandler(e) {

        const newNotif = JSON.parse(e.data)
        let skip = (currentUser.id == newNotif.params.author.id)

        if (!skip) {
            updateDOMForNotifications([ newNotif ])
            receivedNotifications.push(newNotif)
        }
    }

    /* updateDOM() state variable */
    const notificationsContainer = $('<ul class="media-list"></ul>')

    function updateDOMForNotifications(notifs) {

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
          var thereIsAnUnseenNotif = false;

          for (var i=notifs.length-1; i>=0; i--) {

              const templateParams = getTemplateParams(notifs[i])

              element = $(notifItemTemplate
                          .replace('%redirect_url%', templateParams.redirect_url)
                          .replace('%icon_src%', templateParams.icon_src)
                          .replace('%title%', templateParams.title)
                          .replace('%content%', templateParams.content)
                          .replace('%date%', templateParams.date))

              notificationsContainer.prepend(element)

              thereIsAnUnreadNotif = (notifs[i].seen.indexOf('' + currentUser.id) < 0)
          }

          if (thereIsAnUnreadNotif)
              $('#bellicon').css('color', '#f58025')

          $('#bellicon').attr('data-content', $('<div></div>').append(notificationsContainer).html())

          if ($('div.popover.fade.bottom.in').length) { // if popover is open
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
                addNewClassForumThreadTempParams(templateParams, newNotif)
            break

            case 'new_private_forum_message':
            case 'new_public_forum_message':
            case 'new_class_forum_message':
                addNewForumMsgTempParams(templateParams, newNotif)
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

    function addNewClassForumThreadTempParams(templateParams, newNotif) {

        templateParams.redirect_url = '/forum/thread/' + newNotif.params.thread_id
        templateParams.icon_src = '/static/img/icons/forum.png'
        templateParams.title = 'Forum: nouvelle discussion de classe'
        templateParams.content = newNotif.params.author.first_name + ' '
          + newNotif.params.author.last_name
          + ' a créé une nouvelle discussion dans votre classe: '
          + (newNotif.type == 'new_class_forum_thread' ?
            ('<span class="notif-item-emph">' + newNotif.params.class.name + '</span>')
            : ('<span class="notif-item-emph">' + newNotif.params.classes.filter(
              c => c.id == newNotif.server_group.split('-').pop())[0].name +  '</span>'))
    }

    function addNewForumMsgTempParams(templateParams, newNotif) {

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
