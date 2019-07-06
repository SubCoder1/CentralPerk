$('document').ready(function() {
    // login-loading-gif remains hidden till login-btn is clicked
    $('#loading-gif').attr('hidden', 'true');

    // JS Function to accquire the csrftoken
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    var input_username = document.getElementById('login-username');
    var input_pass = document.getElementById('login-pass');
    var error = document.getElementById('form-error');
    var login_btn = document.getElementById('login-btn');

    var togglebutton = function() {
        $('#login-btn').attr('title', '');
    };

    login_btn.addEventListener('click', function(event) {
        // show the loading-screen-gif
        $('#loading-gif').removeAttr('hidden');
        event.preventDefault();
        $.ajax({
            url : '',
            type : "POST",
            data : {
                csrfmiddlewaretoken : csrftoken,
                username : input_username.value,
                password : input_pass.value,
            },

            beforeSend : togglebutton,

            complete : function(response) {
                if (response.responseJSON == 'valid user') {
                    window.location.href += 'home/';
                } else {
                    $('#loading-gif').attr('hidden', 'true');
                    error.innerHTML = "Username or Password is incorrect";
                }
            }
        });
    });
});