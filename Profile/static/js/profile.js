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
            activity: "get_activity",
        }, // data sent with the post request

        // handle a successful response
        complete : function(response) {
            // Using complete in AJAX to check whether the previous request successfully executed or not. 
            // console.log(response.responseJSON);  // log the returned json to the console
            render = document.getElementById('id_activity');
            if (response.responseJSON == "online") {
                render.innerHTML = "<h3><i class='material-icons' style='color:#adff2f; font-size:8px'>lens</i></h3>";
                render.innerHTML += "<h4 style='opacity: 0.5'>Activity</h4>";
                setTimeout(get_user_activity, 1000);
            } else if (response.responseJSON == "#") {
            
            } else {
                render.innerHTML = "<h3>" + response.responseJSON + "</h3>";
                render.innerHTML += "<h4 style='opacity: 0.5'>Activity</h4>";
                setTimeout(get_user_activity, 1000);
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

$(document).ready(function(){
    console.log("firing request to get user activity");
    setTimeout(get_user_activity, 1000);
});