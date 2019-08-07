$(document).ready(function() {
    var homeSocket = new ReconnectingWebSocket(
        'ws://' + window.location.host + '/ws/home/');

    homeSocket.onopen = function(event) {
        // console.log(event);
    }
    
    homeSocket.onmessage = function(server_response) {
        var data = JSON.parse(server_response.data);
        if (data['type'] == 'likes_count') {
            var post_id = '#' + data['post_id'];
            console.log(post_id);
            $(post_id).children('.card-footer').children('.upper-row').children('.likes-counter').text(data['count']);
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
});