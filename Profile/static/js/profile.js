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

function get_user_activity() {
    $.ajax({
        url : username,// the endpoint
        type : "POST", // http method
        data : { 
            csrfmiddlewaretoken: csrftoken,
            activity: "get_user_activity",
        }, // data sent with the post request

        // handle a successful response
        complete : function(response) {
            // Using complete in AJAX to check whether the previous request successfully executed or not. 
            // console.log(response.responseJSON);  // log the returned json to the console
            render = document.getElementById('id_activity');
            if (!response.responseJSON) {
                // Case 1 -- corner case when the activity of the user to be accquired is not being followed.
                // In that case, do nothing and stop the ajax requests being sent to the server every second.
            }
            else if (response.responseJSON == "online") {
                // Case 2 -- The user activity to be checked is being followed and is online ATM.
                render.innerHTML = "<h3><i class='material-icons' style='color:#adff2f; font-size:8px'>lens</i></h3>";
                render.innerHTML += "<h4 style='opacity: 0.5'>Activity</h4>";
                setTimeout(get_user_activity, 2000);
            } else if (response.responseJSON == "#") {
                // Case 3 -- The user is in his/her own profile page.
                // In that case, No need to check continuously and show logged-in user activity.
            } else {
                // Case 4 -- The user activity to be checked is being followed but isn't online ATM.
                render.innerHTML = "<h3>" + response.responseJSON + "</h3>";
                render.innerHTML += "<h4 style='opacity: 0.5'>Activity</h4>";
                setTimeout(get_user_activity, 2000);
            };
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};

function get_user_account_settings() {
    $.ajax({
        url : username,
        type : "POST",
        data : { 
            csrfmiddlewaretoken: csrftoken,
            activity: "get_user_acc_settings",
        }, // data sent with the post request

        complete : function(response) {
            $('#loading-gif').attr('hidden', 'true');
            if (response.responseJSON['disable_all'] == true) {
                $('#disable-all-switch').prop("checked", true);
                $('#post-settings').css("pointer-events", "none");
                $('#post-settings').css("opacity", "0.5");
            } else {
                $('#disable-all-switch').prop("checked", false);
                $('#post-settings').css("pointer-events", "all");
                $('#post-settings').css("opacity", "1");
            }
                var p_likes = response.responseJSON['p_likes'];
                var p_comments = response.responseJSON['p_comments'];
                var p_comment_likes = response.responseJSON['p_comment_likes'];
                var f_req = response.responseJSON['f_requests'];
                if (p_likes == 'Disable') {
                    $('#disable-p-like-radio').prop("checked", true);
                } else if (p_likes == 'From People I Follow') {
                    $('#p-like-from-following-radio').prop("checked", true);
                } else {
                    $('#p-like-from-every-radio').prop("checked", true);
                }

                if (p_comments == 'Disable') {
                    $('#disable-p-c-radio').prop("checked", true);
                } else if (p_comments == 'From People I Follow') {
                    $('#p-c-from-following-radio').prop("checked", true);
                } else {
                    $('#p-c-from-every-radio').prop("checked", true);
                }

                if (p_comment_likes == 'Disable') {
                    $('#disable-p-c-l-radio').prop("checked", true);
                } else if (p_comment_likes == 'From People I Follow') {
                    $('#p-c-l-following-radio').prop("checked", true);
                } else {
                    $('#p-c-l-from-every-radio').prop("checked", true);
                }

                if (f_req == true) { $('#disable-f-switch').prop("checked", true); }
                else { $('#disable-f-switch').prop("checked", false); }
        }
    });
};

function set_user_acc_settings() {
    $.ajax({
        url : username,
        type : "POST",
        data : {
            csrfmiddlewaretoken: csrftoken,
            activity: "set_user_acc_settings",
            disable_all : $('#disable-all-switch').prop("checked"),
            p_likes : $("input[name='p-likes']:checked", '#user_acc_settings_form').val(),
            p_comments : $("input[name='p-comments']:checked", '#user_acc_settings_form').val(),
            p_comment_likes : $("input[name='p-c-likes']:checked", '#user_acc_settings_form').val(),
            f_requests : $('#disable-f-switch').prop("checked"),
        },
    });
};

$(document).ready(function(){
    $('#loading-gif').attr('hidden', 'true');
    setTimeout(get_user_activity, 1000);
    // Get the current user account settings when settings-btn is clicked
    $('#user-acc-settings-btn').click(function() {
        $('#loading-gif').removeAttr('hidden');
        event.preventDefault();
        get_user_account_settings();
    });

    $('#acc_settings_close').click(function(event) {
        $("#user_acc_settings_form").change(function(event) {
            event.preventDefault();
            if ($('#disable-all-switch').prop("checked") == true) {
                $('#post-settings').css("pointer-events", "none");
                $('#post-settings').css("opacity", "0.5");
            } else {
                $('#post-settings').css("pointer-events", "all");
                $('#post-settings').css("opacity", "1");
            }
            set_user_acc_settings();
        });
    })
});