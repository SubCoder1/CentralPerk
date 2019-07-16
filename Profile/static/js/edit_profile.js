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

$(document).ready(function() {
    // Initialize datepicker for birthdate field
    $.fn.datepicker.defaults.format = "dd-mm-yyyy";
    $('.datepicker').datepicker({ format: 'dd-mm-yyyy' });
    // Fill textbox of bio with existing user-input data (if any)
    var $user_bio = $('#user-bio').text();
    $('#edit-bio').val($user_bio.slice(1, $user_bio.length-1));

    // Preview selected profile pic (if selected) before uploading
    var $real_upload_btn = $('#real-file');
    var $custom_upload = $('#custom-upload');
    function previewPIC(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function(e) {
              $custom_upload.attr('src', e.target.result);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }

    $custom_upload.on('click', function() {
        $real_upload_btn.click();
    });

    $real_upload_btn.change(function() {
        previewPIC(this);
        console.log($real_upload_btn[0]);
    });

    var $edit_username = $('#edit-username');
    var $username_error = $('#form-error-username');
    var $edit_fullname = $('#edit-fullname');
    var $fullname_error = $('#form-error-fullname');
    var $edit_email = $('#edit-email');
    var $email_error = $('#form-error-email');
    var $edit_gender = $('#edit-gender');
    var $gender_error = $('#form-error-gender');
    // ajax code to deliver updated data on edit_profile_form submit to server
    $('#edit-prof-form').on('submit', function(event) {
        event.preventDefault();
        $('#edit-prof-loading-gif').toggleClass("loading-gif-active");
        var form = $('#edit-prof-form')[0];
        var data = new FormData(form);
        data.append("activity", "validate_profile_data");
        data.append("profile_pic", $('input[type=file]')[0].files[0]);
        $.ajax({
            url : '',
            type : 'POST',
            enctype: 'multipart/form-data',
            processData: false,  // Important!
            contentType: false,
            cache: false,
            data : data,
            complete : function(response) {
                $('#edit-prof-loading-gif').removeClass("loading-gif-active");
                var status = response.responseJSON;
                if (status == 'valid edit_prof_form') {
                    $('.notify').toggleClass("success-notif-active");
                    setTimeout(function(){
                        $(".notify").removeClass("success-notif-active");
                    }, 2000);
                } else {
                    if (status['username']) {
                        $edit_username.css('border-bottom', '2.5px solid #fc581b');
                        $username_error.text(status['username']);
                    } if (status['full_name']) {
                        $edit_fullname.css('border-bottom', '2.5px solid #fc581b');
                        $fullname_error.text(status['full_name']);
                    } if (status['email']) {
                        $edit_email.css('border-bottom', '2.5px solid #fc581b');
                        $email_error.text(status['email']);
                    } if (status['birthdate']) {
                        $('#edit-birthdate').css('border-bottom', '2.5px solid #fc581b');
                        $('#form-error-birthdate').text(status['birthdate']);
                    } if (status['gender']) {
                        $edit_gender.css('border-bottom', '2.5px solid #fc581b');
                        $gender_error.text(status['gender']);
                    } if (status['bio']) {
                        $('#edit-bio').css('border-bottom', '2.5px solid #fc581b');
                        $('#form-error-bio').text(status['bio']);
                    }
                }
            }
        });
    });

    $('#change_pass-tab').on('click', function() {
        var $old_password = $('#edit-old-password');
        var $old_pass_error = $('#form-error-old-pass');
        var $new_password1 = $('#edit-new-password1');
        var $new_pass1_error = $('#form-error-new-pass1');
        var $new_password2 = $('#edit-new-password2');
        var $new_pass2_error = $('#form-error-new-pass2');
        // ajax code to deliver updated password on change_password_form submit
        $('#change-pass-form').on('submit', function(event) {
            event.preventDefault();
            $('#change-pass-loading-gif').toggleClass("loading-gif-active");
            var flag = true;
            if ($old_password.val() == '') {
                flag = false;
                $old_password.css('border-bottom', '2.5px solid #fc581b');
                $old_pass_error.text("This field cannot be empty");
            } else {
                $old_password.css('border-bottom', '2.5px solid mediumturquoise');
                $old_pass_error.text("");
            }
            
            if ($new_password1.val() == '') {
                flag = false;
                $new_password1.css('border-bottom', '2.5px solid #fc581b');
                $new_pass1_error.text("This field cannot be empty");
            } else {
                $new_password1.css('border-bottom', '2.5px solid mediumturquoise');
                $new_pass1_error.text("");
            }
            
            if ($new_password2.val() == '') {
                flag = false;
                $new_password2.css('border-bottom', '2.5px solid #fc581b');
                $new_pass2_error.text("This field cannot be empty");
            } else {
                $new_password2.css('border-bottom', '2.5px solid mediumturquoise');
                $new_pass2_error.text("");
            }

            if (flag) {
                $.ajax({
                    url : '',
                    type : 'POST',
                    data : {
                        csrfmiddlewaretoken : csrftoken,
                        activity : "validate_new_password",
                        old_password : $old_password.val(),
                        new_password1 : $new_password1.val(),
                        new_password2 : $new_password2.val(),
                    },
                    complete : function(response) {
                        $('#change-pass-loading-gif').removeClass("loading-gif-active");
                        var status = response.responseJSON;
                        if (status == 'valid change_pass_form') {
                            $('.notify').toggleClass("success-notif-active");
                            setTimeout(function(){
                                $(".notify").removeClass("success-notif-active");
                            }, 2000);
                        } else {
                            if (status['old_password']) {
                                $old_password.css('border-bottom', '2.5px solid #fc581b');
                                $old_pass_error.text("Incorrect password"); }
                            if (status['new_password1']) {
                                $new_password1.css('border-bottom', '2.5px solid #fc581b');
                                $new_pass1_error.text(status['new_password1']); }
                            if (status['new_password2']) {
                                $new_password2.css('border-bottom', '2.5px solid #fc581b');
                                $new_pass2_error.text(status['new_password2']); }
                        }
                    }
                });
            }
        });
    })
});