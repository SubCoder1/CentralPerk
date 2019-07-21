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
var username = JSON.parse(document.getElementById('profile_name').textContent);
var bio_more = document.getElementById('more');
var bio_switch = document.getElementById('more-bio-content');
var $user_acc_settings_form = $("#user_acc_settings_form");
var $disable_all_switch = $('#disable-all-switch');
var $disable_f_switch = $('#disable-f-switch');
var $post_settings = $('#post-settings');

function rearrange_profile_bio() {
    var prof_bio = JSON.parse(document.getElementById('profile_bio').textContent);
    var less = document.getElementById('less');
    var newline_count = (prof_bio.match(/\r\n/g) || '').length + 1;
    if (newline_count) {
        var lines = prof_bio.split("\r\n");
        var content = lines.slice(0,lines.length);
        if (lines.length <= 6) {
            for (var i=0; i < content.length; i++) { less.innerHTML += content[i] + '<br/>'; }
        } else {
            for(var i=0; i < 6; i++) { less.innerHTML += content[i] + '<br/>'; }
            for (var i=6; i < content.length; i++) { bio_more.innerHTML += content[i] + '<br/>'; }
            bio_switch.style.display = 'block';
        }
    }
};

function get_user_account_settings() {
    var $account_settings_loading_gif = $('.account-settings-loading-gif');

    var $disable_p_like = $('#disable-p-like-radio');
    var $p_like_from_following = $('#p-like-from-following-radio');
    var $p_like_from_every = $('#p-like-from-every-radio');

    var $disable_p_comments = $('#disable-p-c-radio');
    var $p_c_from_following = $('#p-c-from-following-radio');
    var $p_c_from_every = $('#p-c-from-every-radio');

    var $disable_p_c_like = $('#disable-p-c-l-radio');
    var $p_c_l_from_following = $('#p-c-l-following-radio');
    var $p_c_l_from_every = $('#p-c-l-from-every-radio');

    $.ajax({
        url : username,
        type : "POST",
        data : { 
            csrfmiddlewaretoken: csrftoken,
            activity: "get_user_acc_settings",
        }, // data sent with the post request

        complete : function(response) {
            $account_settings_loading_gif.removeClass("loading-gif-active");
            $user_acc_settings_form.css('display', 'block');
            
            if (response.responseJSON['disable_all'] == true) {
                $disable_all_switch.prop("checked", true);
                $post_settings.css("pointer-events", "none");
                $post_settings.css("opacity", "0.5");
            } else {
                $disable_all_switch.prop("checked", false);
                $post_settings.css("pointer-events", "all");
                $post_settings.css("opacity", "1");
            }
                var p_likes = response.responseJSON['p_likes'];
                var p_comments = response.responseJSON['p_comments'];
                var p_comment_likes = response.responseJSON['p_comment_likes'];
                var f_req = response.responseJSON['f_requests'];
                if (p_likes == 'Disable') {
                    $disable_p_like.prop("checked", true);
                } else if (p_likes == 'From People I Follow') {
                    $p_like_from_following.prop("checked", true);
                } else {
                    $p_like_from_every.prop("checked", true);
                }

                if (p_comments == 'Disable') {
                    $disable_p_comments.prop("checked", true);
                } else if (p_comments == 'From People I Follow') {
                    $p_c_from_following.prop("checked", true);
                } else {
                    $p_c_from_every.prop("checked", true);
                }

                if (p_comment_likes == 'Disable') {
                    $disable_p_c_like.prop("checked", true);
                } else if (p_comment_likes == 'From People I Follow') {
                    $p_c_l_from_following.prop("checked", true);
                } else {
                    $p_c_l_from_every.prop("checked", true);
                }

                if (f_req == true) { $disable_f_switch.prop("checked", true); }
                else { $disable_f_switch.prop("checked", false); }
        }
    });
};

function set_user_acc_settings() {
    var $p_likes = $("input[name='p-likes']:checked", '#user_acc_settings_form');
    var $p_comments = $("input[name='p-comments']:checked", '#user_acc_settings_form');
    var $p_comment_likes = $("input[name='p-c-likes']:checked", '#user_acc_settings_form');
    $.ajax({
        url : username,
        type : "POST",
        data : {
            csrfmiddlewaretoken: csrftoken,
            activity: "set_user_acc_settings",
            disable_all : $disable_all_switch.prop("checked"),
            p_likes : $p_likes.val(),
            p_comments : $p_comments.val(),
            p_comment_likes : $p_comment_likes.val(),
            f_requests : $disable_f_switch.prop("checked"),
        },
        complete : function() {},
        error : function() { 
            //console.log("failure");
        }
    });
};

$(document).ready(function(){
    // Manage oveflowing(if) profile bio
    rearrange_profile_bio();

    // profile-bio read-more read-less toggle
    bio_switch.addEventListener('click', function() {
        if (bio_more.style.display == 'block') {
            bio_more.style.display = 'none';
            bio_switch.innerText = 'Read more...';
        } else {
            bio_more.style.display = 'block';
            bio_switch.innerText = 'Read less...';
        }
    });

    // Get the current user account settings when settings-btn is clicked
    var $user_acc_settings_btn = $('#user-acc-settings-btn');
    var $acc_settings_loading_gif = $('.account-settings-loading-gif');
    $user_acc_settings_btn.click(function() {
        $acc_settings_loading_gif.toggleClass("loading-gif-active");
        $user_acc_settings_form.css('display', 'none');
        get_user_account_settings();
    });

    // Set the current user account settings when user_account_settings_form is changed
    var $disable_all_switch = $('#disable-all-switch');
    var $post_settings = $('#post-settings');
    $user_acc_settings_form.change(function() {
        if ($disable_all_switch.prop("checked") == true) {
            $post_settings.css({"pointer-events":"none", "opacity":"0.5"});
        } else {
            $post_settings.css({"pointer-events":"all", "opacity":"1"});
        }

        set_user_acc_settings();
        var $indicator = $('.indicator');
        $indicator.toggleClass("notif-active");
        setTimeout(function(){
            $indicator.removeClass("notif-active");
        }, 2000);
    });
});