$(document).ready(function() {
    var homeSocket = new ReconnectingWebSocket(
        'ws://' + window.location.host + '/ws/home/');
    
    homeSocket.maxReconnectAttempts = 5;

    homeSocket.onopen = function(event) {
        // console.log(event);
    }
    
    var $wrap_search = $('.wrap-search-res');
    var $notif_wrapper = $('.notif-wrapper');
    var $new_notif_indicator = $('.new-notif-indicator');
    var $post_container = $('.post-container');
    var $wrap_update_posts = $('#update-posts');
    var $p_chat_cover_wrapper = $('.p-chat-cover-wrapper');
    var $followers_wrapper = $('.followers-wrapper');
    var $following_wrapper = $('.following-wrapper');
    var $p_chat_notif_wrapper = $('.p-chat-notif-wrapper');
    var $p_chat_seen = null;

    homeSocket.onmessage = function(server_response) {
        var data = JSON.parse(server_response.data);
        // Update likes count for a particular post
        if (data['type'] == 'likes_count') {
            var post_id = '#' + data['post_id'];
            $(post_id).children('.card-footer').children('.upper-row').children('.likes-counter').text(data['count']);
        }
        // Update comment count for a particular post 
        else if (data['type'] == 'comment_count') {
            var post_id = '#' + data['post_id'];
            $(post_id).children('.card-footer').children('.upper-row').children('.comment-counter').text(data['count']);
        }
        // Update notifications wrapper
        else if (data['type'] == 'updated_notif') {
            $new_notif_indicator.css('display', 'block');
            $notif_wrapper.html(data['notif']);
        }
        // Update wall
        else if (data['type'] == 'updated_wall') {
            $wrap_update_posts.css('display', 'flex');
            $wrap_update_posts.on('click', function() {
                $("body").scrollTop(0);
                if (data) {
                    if (data['posts']) {
                        $post_container.html(data['posts']);
                        $post_container.trigger('contentchanged');
                    }
                }
                $(this).css('display', 'none');
            });
        }
        // Display search result
        else if (data['type'] == 'search_results') {
            $wrap_search.html(data['results']);
        }
        // Display p_chat_cover
        else if (data['type'] == 'p_chat_cover_f_server') {
            $p_chat_cover_wrapper.html(data['p-chat-cover']);
        }
        // Display p_chat
        else if (data['type'] == 'p_chat_f_server') {
            $p_chat_cover_wrapper.html(data['p-chat']);
        }
        // Display msg sent from server
        else if (data['type'] == 'p_chat_msg_f_server') {
            if ($('.p-chat-modal-body').is("#"+data['convo_id'])) {
                var new_txt = "<div class='animate-txt-wrap' style='justify-content: flex-end; flex-direction: column;'>\
                <div class='wrap-p-chat-txt rec-txt-wrapper'><h6 class='p-chat-rec-txt'>" + data['msg'] + "</h6></div>"
                + "<h6 class='p-chat-rec-date-time'>" + data['date_time'] + "</h6></div>";
                var $data = $(new_txt);
                $('.p-chat-modal-body').append($data);
                $('.p-chat-modal-body').animate({
                    scrollTop: $('.p-chat-modal-body').get(0).scrollHeight
                }, 1500);
                $data.animate({'margin-top': '10px'}, 230);   
            }
        }
        // Display seen signal in p_chat
        else if (data['type'] == 'p_chat_msg_seen') {
            if ($('.p-chat-modal-body').is("#"+data['convo_id'])) {
                if ($p_chat_seen != null) {
                    $p_chat_seen.remove();
                }
                $p_chat_seen = $("<h6 class='p-chat-seen'>👀</h6>");
                $('.p-chat-modal-body').append($p_chat_seen);
                $('.p-chat-modal-body').animate({
                    scrollTop: $('.p-chat-modal-body').get(0).scrollHeight
                }, 1500);
                $p_chat_seen.animate({'margin-top': '10px'}, 230);
            }
        }
        // Display notif to user that someone has sent a msg
        else if (data['type'] == 'p_chat_notif_f_server') {
            $p_chat_notif_wrapper.html(data['p_chat_notif']);
            setTimeout(function(){
                $p_chat_notif_wrapper.empty();
            }, 2000);
        }
        // Update p_chat
        else if (data['type'] == 'update_p_chat') {
            var $p_chat_activity_div = $('#'+data['unique_id']);
            if ($p_chat_activity_div != null) {
                if (data['activity'] == 'login') {
                    $p_chat_activity_div.html("<i class='material-icons online-green-ico'>lens</i>");
                } else {
                    $p_chat_activity_div.html("<h5 class='p-chat-last-login'>a few seconds ago</h5>");
                }
            }
        }
        // Display friends list
        else if (data['type'] == 'friends_list_f_server') {
            $followers_wrapper.html(data['followers']);
            $following_wrapper.html(data['following']);
        }
    };

    homeSocket.onclose = function() {
        console.error("Socket closed unexpectedly!");
    };

    // Like posts from wall
    var $wall_post_like_btn = $('.wall-post-like');
    $wall_post_like_btn.on('click', function(event) {
        event.preventDefault();
        var post_id = $(this).closest('.card').attr('id');
        homeSocket.send(JSON.stringify({
            'task' : 'post_like',
            'post_id' : post_id,
        }));
    });

    // Save/Unsave Posts from wall
    var $post_bookmark = $('.lnr-bookmark');
    $post_bookmark.on("click", function(event) {
        event.preventDefault();
        var post_id = $(this).closest('.card').attr('id');
        homeSocket.send(JSON.stringify({
            'task' : 'save_unsave_post',
            'post_id' : post_id,
        }));
    });

    // Send posted comments from wall
    var $wall_comment_form = $('.wall-comment-form');
    $wall_comment_form.on('submit', function(event) {
        event.preventDefault();
        var post_id = $(this).children('input').val();
        var comment = $(this).children('textarea').val();
        homeSocket.send(JSON.stringify({
            'task' : 'post_comment',
            'post_id' : post_id,
            'comment' : comment,
        }));
        $(this).children('textarea').val("");
    });

    // Get notifications
    var $get_notif = $('.notif-btn');
    $get_notif.on('click', function(event) {
        event.preventDefault();
        if ($get_notif.hasClass('updated') == false) {
            var $notif_wrapper = $('.notif-wrapper');
            $notif_wrapper.html("<img class='modal-loading-gif loading-gif-active' src='/static/img/loading.gif'/>");
            homeSocket.send(JSON.stringify({
                'task' : 'get_notifications',
            }));
        }
    });

    // Clear all notifications
    var $clear_notify = $('.clear-notify');
    $clear_notify.on('click', function(event) {
        event.preventDefault();
        homeSocket.send(JSON.stringify({
            'task' : 'clear_notif_all',
        }));
    });

    // Send Search query to server
    var $search_bar = $('.search-bar');
    $search_bar.on('input', function(event) {
        if ($search_bar.val() == '') {
            $wrap_search.html("");
        } else {
            homeSocket.send(JSON.stringify({
                'task' : 'search',
                'query' : $search_bar.val(),
            }));
        }
    });

    // Accept/Reject private friend requests
    var $accept_request = $('.accept-request');
    $accept_request.on('click', function(event) {
        event.preventDefault();
        homeSocket.send(JSON.stringify({
            'task' : 'accept_reject_p_request',
            'notif_id' : $(this).attr('id'),
            'option' : 'accept_request',
        }));
        $(this).parent().parent().parent().fadeOut(300, function(){ $(this).remove();});;
    });
    var $reject_request = $('.reject-request');
    $reject_request.on('click', function(event) {
        event.preventDefault();
        homeSocket.send(JSON.stringify({
            'task' : 'accept_reject_p_request',
            'notif_id' : $(this).attr('id'),
            'option' : 'reject_request',
        }));
        $(this).parent().parent().parent().fadeOut(300, function(){ $(this).remove();});;
    });

    // Get friends list
    var $online_users_btn = $('.online-users-btn');
    $online_users_btn.on('click', function(event) {
        event.preventDefault();
        if ($online_users_btn.hasClass('updated') == false) {
            var $followers_wrapper = $('.followers-wrapper');
            var $following_wrapper = $('.following-wrapper');
            $followers_wrapper.html("<img class='modal-loading-gif loading-gif-active' src='/static/img/loading.gif'/>");
            $following_wrapper.html("<img class='modal-loading-gif loading-gif-active' src='/static/img/loading.gif'/>");
            homeSocket.send(JSON.stringify({
                'task' : 'get_friends_list',
            }));
        }
    });

    // CHAT SECTION

    // Send req to get p-chat-cover
    var $chat_btn = $('.chat-btn');
    $chat_btn.on('click', function(event) {
        event.preventDefault();
        if ($p_chat_cover_wrapper.children().hasClass('p-chat-upper-card') == false) {
            homeSocket.send(JSON.stringify({
                'task' : 'get_p_chat_cover',
            }));
        }
    });
    // Same event on clicking the back btn on p-chat
    $p_chat_cover_wrapper.on('click', '.p-chat-cover-b-link', function(event) {
        event.preventDefault();
        $p_chat_cover_wrapper.html("<img class='modal-loading-gif loading-gif-active' src='/static/img/loading.gif'/>");
        homeSocket.send(JSON.stringify({
            'task' : 'get_p_chat_cover',
        }));
    })
    
    // Send req to get p-chat
    $p_chat_cover_wrapper.on('click', '.msg-user-card', function(event) {
        var username = $(this).attr('id');
        $p_chat_cover_wrapper.html("<img class='modal-loading-gif loading-gif-active' src='/static/img/loading.gif'/>");
        homeSocket.send(JSON.stringify({
            'task' : 'get_p_chat',
            'user' : username,
        }));
    });
    
    // Send msg in p-chat
    $p_chat_cover_wrapper.on('click', '.p-chat-snd-btn', function(event) {
        event.preventDefault();
        if (/\S/.test($('.p-chat-txtbox').val())) {
            var new_txt = "<div class='animate-txt-wrap'><div class='wrap-p-chat-txt'><h6 class='p-chat-sent-txt'>" + $('.p-chat-txtbox').val() + "</h6></div>";
            var send_anim = "<i class='far fa-paper-plane'></i></div>";
            var date_time = new Date($.now()).toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });
            var d_t_data = "<h6 class='p-chat-snd-date-time'>"+date_time+"</h6>";
            var $data = $(new_txt+send_anim);

            $('.p-chat-modal-body').append($data);
            $('.p-chat-modal-body').append(d_t_data);
            $('.p-chat-modal-body').animate({
                scrollTop: $('.p-chat-modal-body').get(0).scrollHeight
            }, 1500);
            $data.animate({'margin-top': '10px'}, 230);


            var convo_id = $('.p-chat-modal-body').attr('id');
            homeSocket.send(JSON.stringify({
                'task' : 'p_chat_msg',
                'msg' : $('.p-chat-txtbox').val(),
                'convo_id' : convo_id,
                'date_time' : date_time,
            }));

            $('.p-chat-txtbox').val("");
            setTimeout(function(){
                $('.fa-paper-plane').remove();
            }, 400);
        }
    });
});