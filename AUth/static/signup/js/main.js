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

    var username_error = $('#form-error-username');
    var register_username = $('#register-username');
    register_username.change(function(event) {
        event.preventDefault();
        if(/^[a-zA-Z0-9- ]*$/.test(register_username.val()) == false) {
            register_username.css('border-bottom', '2.5px solid #fc581b');
            username_error.text("Username should only contain letters & numbers");
        }
        else if (register_username.val().length < 5) {
            register_username.css('border-bottom', '2.5px solid #fc581b');
            username_error.text("Username should be > 6 characters");
        } else if (register_username.val().length > 20) {
            register_username.css('border-bottom', '2.5px solid #fc581b');
            username_error.text("Username should be < 21 characters");
        } else if (register_username.val().indexOf(' ') > -1) {
            register_username.css('border-bottom', '2.5px solid #fc581b');
            username_error.text("Username should consist only characters");
        }
        else {
            $.ajax({
                url : '',
                type : 'POST',
                data : {
                    csrfmiddlewaretoken : csrftoken,
                    username : register_username.val(),
                    activity : 'check username validity',
                },

                complete : function(response) {
                    if (response.responseJSON == 'valid username') {
                        register_username.css('border-bottom', '2.5px solid springgreen');
                        username_error.text("");
                    } else {
                        register_username.css('border-bottom', '2.5px solid #fc581b');
                        username_error.text(response.responseJSON);
                    }
                }
            });
        }
    });

    var fullname_error = $('#form-error-fullname');
    var register_fullname = $('#register-fullname');
    register_fullname.change(function(event) {
        event.preventDefault();
        if (/^[a-zA-Z0-9- ]*$/.test(register_fullname.val()) == false || register_fullname.val().length == 0 || /\d/.test(register_fullname.val())) {
            register_fullname.css('border-bottom', '2.5px solid #fc581b');
            fullname_error.text("Full name should contain only letters");
        } else if (register_fullname.val().length > 50) {
            register_fullname.css('border-bottom', '2.5px solid #fc581b');
            fullname_error.text("Full name should be < 51 characters");
        }
        else {
            register_fullname.css('border-bottom', '2.5px solid springgreen');
            fullname_error.text("");
        }
    });

    var email_error = $('#form-error-email');
    var register_email = $('#register-email');
    register_email.change(function(event) {
        event.preventDefault();
        if (register_email.val().length > 254) {
            register_email.css('border-bottom', '2.5px solid #fc581b');
            email_error.text("Email should be < 255 characters");
        } else {
            $.ajax({
                url : '',
                type : 'POST',
                data : {
                    csrfmiddlewaretoken : csrftoken,
                    email : register_email.val(),
                    activity : 'check email validity',
                },

                complete : function(response) {
                    if (response.responseJSON == 'valid email') {
                        register_email.css('border-bottom', '2.5px solid springgreen');
                        email_error.text("");
                    } else {
                        register_email.css('border-bottom', '2.5px solid #fc581b');
                        email_error.text(response.responseJSON);
                    }
                }
            });
        }
    });

    var register_gender = $('#register-gender');
    var gender_error = $('#form-error-gender');
    register_gender.change(function() {
        register_gender.css('border-bottom', '2.5px solid springgreen');
        gender_error.text("");
    });

    var pass_error = $('#form-error-password');
    var register_pass = $('#register-pass');
    register_pass.change(function(event) {
        event.preventDefault();
        $.ajax({
            url : '',
            type : 'POST',
            data : {
                csrfmiddlewaretoken : csrftoken,
                username : register_username.val(),
                email : register_email.val(),
                password : register_pass.val(),
                activity : 'check pass strength',
            },

            complete : function(response) {
                var strength = response.responseJSON;
                if (strength.includes('medium')) {
                    register_pass.css('border-bottom', '2.5px solid orange');
                    pass_error.text(strength);
                } else if (strength.includes('bad')) {
                    register_pass.css('border-bottom', '2.5px solid #fc581b');
                    pass_error.text(strength);
                } else {
                    register_pass.css('border-bottom', '2.5px solid springgreen');
                    pass_error.text("");
                }
            }
        });
    });

    var signup_btn = document.getElementById('signup-btn');
    var togglebutton = function() {
        $('#signup-btn').attr('title', '');
    }
    
    signup_btn.addEventListener('click', function(event) {
        $('#loading-gif').removeAttr('hidden');
        event.preventDefault();
        $.ajax({
            url : '',
            type : 'POST',
            beforeSend : togglebutton,
            data : {
                csrfmiddlewaretoken : csrftoken,
                activity : 'register user',
                username : register_username.val(),
                email : register_email.val(),
                full_name : register_fullname.val(),
                gender : $('#choice').val(),
                password : register_pass.val(),
            },
            
            complete : function(response) {
                $('#loading-gif').attr('hidden', 'true');
                var status = response.responseJSON;
                if (status['username']) {
                    register_username.css('border-bottom', '2.5px solid #fc581b');
                    username_error.text(status['username']);
                } if (status['full_name']) {
                    register_fullname.css('border-bottom', '2.5px solid #fc581b');
                    fullname_error.text(status['full_name']);
                } if (status['email']) {
                    register_email.css('border-bottom', '2.5px solid #fc581b');
                    email_error.text(status['email']);
                } if (status['gender']) {
                    register_gender.css('border-bottom', '2.5px solid #fc581b');
                    gender_error.text(status['gender']);
                } if(status['password']) {
                    status = String(status['password'])
                    if (status.includes('bad') || status == 'This field is required.') {
                        register_pass.css('border-bottom', '2.5px solid #fc581b');
                    } else if (status.includes('medium')) {
                        register_pass.css('border-bottom', '2.5px solid orange');
                    } else {
                        register_pass.css('border-bottom', '2.5px solid springgreen');
                    }
                    pass_error.text(status);
                } if (status == 'valid form') {
                    window.location.href += 'home/';
                }
            }

        });
    });
});