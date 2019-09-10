$(document).ready(function() {
    var homeSocket = new ReconnectingWebSocket(
        'ws://' + window.location.host + '/ws/home/');

    homeSocket.onopen = function(event) {
        // console.log(event);
    }
    
    var $wrap_search = $('.wrap-search-res');

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
        // Update save/unsave post icon
        else if (data['type'] == 'save_unsave_post_response') {
            var post_id = '#' + data['post_id'];
            var $post_bookmark = $(post_id).children('.card-header').children('.d-flex').children('.wrap-save-post').children('.lnr-bookmark');
            if (data['result'] == 'saved') {
                $post_bookmark.toggleClass('bookmark-saved');
            } else {
                $post_bookmark.removeClass('bookmark-saved');
            } 
        }
        // Update notifications wrapper
        else if (data['type'] == 'updated_notif') {
            var $notif_wrapper = $('.notif-wrapper');
            $notif_wrapper.html(data['notif']);
        }
        // Update friends list
        else if (data['type'] == 'update_friends_list') {
            // console.log("friend_list_updated");
            var $online_wrapper = $('.online-wrapper');
            var $followers_wrapper = $('.followers-wrapper');
            var $following_wrapper = $('.following-wrapper');

            $online_wrapper.html(data['online-users-list']);
            $followers_wrapper.html(data['followers-list']);
            $following_wrapper.html(data['following-list']);
        }
        // Update wall
        else if (data['type'] == 'updated_wall') {
            var $post_container = $('.post-container');
            var $wrap_update_posts = $('#update-posts');
            $wrap_update_posts.css('display', 'block');

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
        $(this).parent().parent().parent().remove();
    });
    var $reject_request = $('.reject-request');
    $reject_request.on('click', function(event) {
        event.preventDefault();
        homeSocket.send(JSON.stringify({
            'task' : 'accept_reject_p_request',
            'notif_id' : $(this).attr('id'),
            'option' : 'reject_request',
        }));
        $(this).parent().parent().parent().remove();
    });

});