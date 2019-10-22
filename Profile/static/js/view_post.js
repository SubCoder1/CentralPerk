$(document).ready(function() {
    // Function to accquire the csrftoken
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    // JS code to set height of comment-view-card-body(comment box in view_post) & like-view-card-body
    const post_card = document.getElementById('id_view-post-card');
    if (post_card) {
        const card_height = parseInt(document.getElementById('id_view-post-card').clientHeight);
        const card_header_height = parseInt(document.getElementById('id_view-post-card-header').clientHeight);
        const card_footer_height = 53;
        const like_card_footer_height = 63;

        var comment_body_height = card_height - (card_header_height + card_footer_height) - 4;
        var like_body_height = card_height - (card_header_height + like_card_footer_height);
        var comment_height = "height:" + comment_body_height.toString() + "px";
        var like_height = "height:" + like_body_height.toString() + "px";
        var details_height = "height:" + (comment_body_height + 37).toString() + "px";

        var comment_body_height = document.getElementById('id_view-post-comment-body');
        var like_body_height = document.getElementById('id_view-post-like-body');
        var details_body_height = document.getElementById('id_view-post-details-body');
        comment_body_height.setAttribute('style', comment_height);
        like_body_height.setAttribute('style', like_height);
        details_body_height.setAttribute('style', details_height);

    };

    // JS code for handling comment replies
    var length = 0;
    var $comment_box = $('#comment_box');
    var $post_comment_wrapper = $('#post-comments-wrapper');
    $post_comment_wrapper.on("click", ".comment-reply", function(event) {
        event.preventDefault();
        var reply_to = $(this).siblings('.m-0').children('a').text().replace(/\s+/g, '');
        $(".reply-to").val($(this).attr('id') + "_" + reply_to);
        $comment_box.val("@" + reply_to + " ");
        length = reply_to.length;
        $comment_box.focus();
    });
    
    // JS code that removes comment-reply-link if reply-to-username is removed from comment-box
    $comment_box.on('input', function() {
        if ($(this).val().length < length+1) {
            $(".reply-to").val("");
        }
        else if ($(this).val() == "") {
            $(".reply-to").val("");
        }
    });

    // Refresh content on refresh-btn click
    var $post_likes_wrapper = $('#post-likes-wrapper');
    var $refresh_content_loading_gif = $('#loading-gif');
    var $refresh_btn = $('#refresh-content');
    var $comment_count = $('#comment_count');
    var $likes_count = $('#likes_count');
    var $indicator = $('.indicator');
    var $success = $('#success-msg');
    var $error = $('#error-msg');
    $refresh_btn.on('click', function(event) {
        event.preventDefault();
        $refresh_btn.css("pointer-events", "none");
        $refresh_content_loading_gif.removeClass('hidden');
        // One request for refreshed-comments
        $.ajax({
            url : "",
            type : "GET",
            data : {
                activity : "refresh comments",
            },
            complete : function(response) {
                $post_comment_wrapper.html(response.responseJSON['post_comments_html']);
                $comment_count.text(response.responseJSON['comment_count']);
                $refresh_btn.css("pointer-events", "all");
            },
            error : function() {
                $indicator.toggleClass("notif-active");
                $error.text("Refresh failed, Try again!");
                $error.removeClass("hidden");
                setTimeout(function(){
                    $indicator.removeClass("notif-active");
                    $error.text("");
                    $error.toggleClass("hidden");
                }, 3000);
            }
        });
        // One request for refreshed-likes
        $.ajax({
            url : "",
            type : "GET",
            data : {
                activity : "refresh likes",
            },
            complete : function(response) {
                $indicator.toggleClass("notif-active");
                $success.text("Successfully refreshed!");
                $success.removeClass("hidden");
                setTimeout(function(){
                    $indicator.removeClass("notif-active");
                    $success.text("");
                    $success.toggleClass("hidden");
                }, 2000);
                $refresh_content_loading_gif.toggleClass('hidden');
                $post_likes_wrapper.html(response.responseJSON['post_likes_html']);
                $likes_count.text(response.responseJSON['likes_count']);
            }, 
            error : function() {
                $indicator.toggleClass("notif-active");
                $error.text("Refresh failed, Try again!");
                $error.removeClass("hidden");
                setTimeout(function(){
                    $indicator.removeClass("notif-active");
                    $error.text("");
                    $error.toggleClass("hidden");
                }, 3000);
            }
        });
    });

    // show/hide comment replies toggle
    var $comment_replies = $('#c-replies-collapse');
    var $c_replies_arrow = $('.fa-angle-down');
    $comment_replies.on('click', function(event) {
        event.preventDefault();
        if ($comment_replies.html().indexOf("hide replies") != -1) {
            $comment_replies.html("show replies <i class='fas fa-angle-down'></i>");
            $(this).children($c_replies_arrow).removeClass('rotate_180');
        } else {
            $comment_replies.html("hide replies <i class='fas fa-angle-down'></i>");
            $(this).children($c_replies_arrow).toggleClass('rotate_180');
        }
    });

    // handle comment_send
    var $comment_send_form = $('#comment_form');
    var $comment_box = $('#comment_box');
    var $comment_body = $('#id_view-post-comment-body');
    $comment_send_form.on('submit', function(event) {
        event.preventDefault();
        $comment_body.css({"opacity":"0.7", "pointer-events":"none"});
        $comment_send_form.css("pointer-events", "none");
        // send comment response to server
        $.ajax({
            url : '',
            type : 'POST',
            data : {
                csrfmiddlewaretoken : csrftoken,
                comment : $comment_box.val(),
                reply : $('#reply').val(),
                activity: "add comment",
            },
            complete : function(response) { 
                $comment_box.val("");
                if (response.responseJSON == 'ready to update') {
                    // another request to update post_comments
                    $comment_count.text(parseInt($comment_count.text()) + 1);
                    $.ajax({
                        url : "",
                        type : "GET",
                        data : {
                            activity : "refresh comments",
                        },
                        complete : function(response) {
                            // disply notify msg to the user
                            $indicator.toggleClass("notif-active");
                            $success.text("Comment successfully posted!");
                            $success.removeClass("hidden");
                            setTimeout(function(){
                                $indicator.removeClass("notif-active");
                                $success.text("");
                                $success.toggleClass("hidden");
                            }, 2000);
                            $comment_body.css({"opacity":"1", "pointer-events":"all"});
                            $comment_send_form.css("pointer-events", "all");
                            $post_comment_wrapper.html(response.responseJSON['post_comments_html']);
                        },
                    });
                } else {
                    // disply notify msg to the user
                    $indicator.toggleClass("notif-active");
                    $error.text("Post unsuccessful, Try again!");
                    $error.removeClass("hidden");
                    setTimeout(function(){
                        $indicator.removeClass("notif-active");
                        $error.text("");
                        $error.toggleClass("hidden");
                    }, 3000);
                    $comment_body.css({"opacity":"1", "pointer-events":"all"});
                    $comment_send_form.css("pointer-events", "all");
               }
            }
        });
    });

    // handle comment_delete
    $post_comment_wrapper.on('click', '.comment-dlt', function(event) {
        event.preventDefault();
        $post_comment_wrapper.css('pointer-events', 'none');
        $.ajax({
            url : '',
            type : 'POST',
            data : {
                csrfmiddlewaretoken : csrftoken,
                activity: "delete comment",
                comment_id : $(this).attr('id'),
            },
            success : function(response) {
                // Update comment-section
                if (response != "post_comment doesn't exist") {
                    $post_comment_wrapper.html(response['post_comments_html']);
                    $comment_count.text(response['comment_count']);
                } else {
                    setTimeout(function(){
                        $indicator.removeClass("notif-active");
                        $error.text("Comment delete unsuccessful!");
                        $error.toggleClass("hidden");
                    }, 3000);
                }
            }, 
            error : function(response) {
                setTimeout(function(){
                    $indicator.removeClass("notif-active");
                    $error.text("Error! Try again");
                    $error.toggleClass("hidden");
                }, 3000);
            }
        });
        $post_comment_wrapper.css('pointer-events', 'all');
    });

    // handle likes send and update
    var $post_like_btn = $('#post_like_btn');
    var $liked_by_user = $('#post_like_btn').children('i');
    var action;
    $post_like_btn.on("click", function(event) {
        event.preventDefault();
        $post_like_btn.css("pointer-events", "none");
        if ($liked_by_user.hasClass('liked')) {
            $liked_by_user.removeClass('liked');
            action = 'disliked';
            $liked_by_user.toggleClass('disliked');
        } else {
            $liked_by_user.removeClass('disliked');
            action = 'liked';
            $liked_by_user.toggleClass('liked');
        }
        // send response to server
        $.ajax({
            url : $post_like_btn.attr("href"),
            type : "POST",
            data : {
                csrfmiddlewaretoken : csrftoken,
                action : action,
            },
            complete : function(response) {
                action = response.responseJSON['action'];
                // liked or disliked post, now update body
                if (response.responseJSON['status'] == 'ready to update') {
                    $.ajax({
                        url : "",
                        type : "GET",
                        data : {
                            activity : "refresh likes",
                        },
                        complete : function(response) {
                            $indicator.toggleClass("notif-active");
                            $success.text(action);
                            $success.removeClass("hidden");
                            setTimeout(function(){
                                $indicator.removeClass("notif-active");
                                $success.text("");
                                $success.toggleClass("hidden");
                                $post_like_btn.css("pointer-events", "all");
                            }, 2000);
                            $post_likes_wrapper.html(response.responseJSON['post_likes_html']);
                            $likes_count.text(response.responseJSON['likes_count']);
                        }
                    });
                } else {
                    $indicator.toggleClass("notif-active");
                    $error.text("Something went wrong, Try again!");
                    $error.removeClass("hidden");
                    setTimeout(function(){
                        $indicator.removeClass("notif-active");
                        $error.text("");
                        $error.toggleClass("hidden");
                        $post_like_btn.css("pointer-events", "all");
                    }, 3000);
                }
            }
        });
    });
});