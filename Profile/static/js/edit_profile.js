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
    // JS code for navbar on-scrolldown animation
    window.onscroll = function() {scrollFunction()};
    var navbar = document.getElementById("navbar");
    var logo = document.getElementById("logo");
    var $brand_name = $('#brand-name');
    var $brand_ico = $('#brand-ico');

    function scrollFunction() {
        if (document.body.scrollTop > 30 || document.documentElement.scrollTop > 30) {
            navbar.style.padding = "8px 68px 0px 68px";
            logo.style.fontSize = "20px";
            $brand_name.hide();
            $brand_ico.css('height', '38px');
        } else {
            navbar.style.padding = "10px 68px 0px 68px";
            logo.style.fontSize = "25px";
            $brand_name.show();
            $brand_ico.css('height', '32px');
        }
    }

    // Initialize datepicker for birthdate field
    $.fn.datepicker.defaults.format = "dd-mm-yyyy";
    $('.datepicker').datepicker({ format: 'dd-mm-yyyy' });
    // Fill textbox of bio with existing user-input data (if any)


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

    var $prof_pic_error = $('#form-error-prof-pic');
    $real_upload_btn.change(function() {
        var $upload_file = $(this).val();
        if ($upload_file != '') {
            var idxDot = $upload_file.lastIndexOf(".") + 1;
            var extFile = $upload_file.substr(idxDot, $upload_file.length).toLowerCase();
            if (extFile=="jpg" || extFile=="jpeg" || extFile=="png"){
                $prof_pic_error.text("");
                previewPIC(this);
            }else{
                $(this).val("");
                $prof_pic_error.text("Only jpg/jpeg and png files are allowed!");
            }
        }
    });

    var $indicator = $('.indicator');
    // ajax code to deliver updated data on edit_profile_form submit to server
    $('#edit-prof-form').on('submit', function(event) {
        event.preventDefault();

        var $prof_pic_error = $('#form-error-prof-pic');
        var $edit_username = $('#edit-username');
        var $username_error = $('#form-error-username');
        var $edit_fullname = $('#edit-fullname');
        var $fullname_error = $('#form-error-fullname');
        var $edit_email = $('#edit-email');
        var $email_error = $('#form-error-email');
        var $edit_birthdate = $('#edit-birthdate');
        var $birthdate_error = $('#form-error-birthdate');
        var $edit_gender = $('#edit-gender');
        var $gender_error = $('#form-error-gender');
        var $edit_bio = $('#edit-bio');
        var $bio_error = $('#form-error-bio');
        var $edit_profile_loading_gif = $('#edit-prof-loading-gif');

        $edit_profile_loading_gif.toggleClass("loading-gif-active");
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
                $edit_profile_loading_gif.removeClass("loading-gif-active");
                if (response.responseJSON) {
                    var status = response.responseJSON;
                } else {
                    var status = response;
                }
                if (status['result'] == 'valid edit_prof_form') {
                    if (status['updated_username']) {
                        $('.nav-username').text(status['updated_username']);
                        $('.drop-nav-username').text(status['updated_username']);
                    }
                    if (status['updated_prof_pic']) {
                        $('.navbar-profile-pic').attr('src', status['updated_prof_pic']);
                    }
                    $username_error.text("");
                    $edit_username.css('border-bottom', '2.5px solid mediumturquoise');
                    $fullname_error.text("");
                    $edit_fullname.css('border-bottom', '2.5px solid mediumturquoise');
                    $email_error.text("");
                    $edit_email.css('border-bottom', '2.5px solid mediumturquoise');
                    $gender_error.text("");
                    $edit_gender.css('border-bottom', '2.5px solid mediumturquoise');
                    $birthdate_error.text("");
                    $edit_birthdate.css('border-bottom', '2.5px solid mediumturquoise');
                    $bio_error.text("");
                    $edit_bio.css('border-bottom', '2.5px solid mediumturquoise');

                    // Success msg popup for 2 seconds
                    $indicator.toggleClass("notif-active");
                    setTimeout(function(){
                        $indicator.removeClass("notif-active");
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
                        $edit_birthdate.css('border-bottom', '2.5px solid #fc581b');
                        $birthdate_error.text(status['birthdate']);
                    } if (status['gender']) {
                        $edit_gender.css('border-bottom', '2.5px solid #fc581b');
                        $gender_error.text(status['gender']);
                    } if (status['bio']) {
                        $edit_bio.css('border-bottom', '2.5px solid #fc581b');
                        $bio_error.text(status['bio']);
                    } if (status['profile_pic']) {
                        $prof_pic_error.text(status['profile_pic']);
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
        var $change_pass_loading_gif = $('#change-pass-loading-gif');
        // ajax code to deliver updated password on change_password_form submit
        $('#change-pass-form').on('submit', function(event) {
            event.preventDefault();
            $change_pass_loading_gif.toggleClass("loading-gif-active");
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

            if (!flag) { $change_pass_loading_gif.removeClass("loading-gif-active"); }

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
                        $change_pass_loading_gif.removeClass("loading-gif-active");
                        var status = response.responseJSON;
                        if (status == 'valid change_pass_form') {
                            $old_password.css('border-bottom', '2.5px solid mediumturquoise');
                            $old_pass_error.text("");
                            $new_password1.css('border-bottom', '2.5px solid mediumturquoise');
                            $new_pass1_error.text("");
                            $new_password2.css('border-bottom', '2.5px solid mediumturquoise');
                            $new_pass2_error.text("");
                            
                            
                            $indicator.toggleClass("success-notif-active");
                            setTimeout(function(){
                                $indicator.removeClass("success-notif-active");
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