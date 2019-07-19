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

// JS code for post-card data overflow management
var elms = document.querySelectorAll("[id='post-data']");
var post_container = document.querySelectorAll("[id='status_caption-container']");
for(var i=0; i < elms.length; i++) {
  (function (i) {
    var post = JSON.parse(elms[i].textContent);
    var newline_count = (post.match(/\r\n/g) || '').length + 1;
    if (newline_count) {
      var lines = post.split("\r\n");
      if (lines.length > 5) {
        var read_less = lines.slice(0,5);
        // var read_more = lines.slice(5,lines.length);
        // console.log(read_less);
        // console.log("-------");
        // console.log(read_more);
        for (var j=0; j < 5; j++) {
          post_container[i].innerHTML += read_less[j] + '<br/>';
        }
        var read_more = post_container[i].getElementsByTagName("a")[0];
        post_container[i].removeChild(read_more);
        var read_more_link = '<a class="body_link read-more" href="' + read_more + '">Read more...</a>'
        post_container[i].innerHTML += read_more_link;
      } else {
        var read_less = lines.slice(0,lines.length);
        for (var j=0; j < lines.length; j++) {
          post_container[i].innerHTML += read_less[j] + '<br/>';
        }
      }
    } else if (post.length > 200) {
      post_container[i].innerHTML += post.slice(0,200);
      var read_more = post_container[i].getElementsByTagName("a")[0];
      post_container[i].removeChild(read_more);
      var read_more_link = '<a class="body_link read-more" href="' + read_more + '"></a>'
      post_container[i].innerHTML += read_more_link;
    } 
    else {
      post_container[i].innerHTML += post;
    }
  }).call(this, i);
}

$(document).ready(function() {
  // JQuery code to clear alert messages on post-success or error
  var $indicator = $('.indicator');
  if ($indicator) {
    $indicator.toggleClass("success-notif-active");
    setTimeout(function(){
      $indicator.removeClass("success-notif-active");
    }, 2000);
  }

  // JQuery code to preview uploaded image and clear it (if clicked on img)
  var $real_upload_btn = $('#real-file');
  var $custom_upload = $('#img-btn-custom');
  var $preview_img = $('#preview-img');
  var $reset_img_ico = $('#reset-img-ico');

  function previewPIC(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
          $preview_img.attr('src', e.target.result);
          $preview_img.css('display', 'block');
        }
        reader.readAsDataURL(input.files[0]);
    }
  }

  $custom_upload.click(function() {
    $real_upload_btn.click();
  });

  $real_upload_btn.change(function() {
    $custom_upload.css('display', 'none');
    previewPIC(this);
  });

  $preview_img.on('click', function() {
    $preview_img.css('display', 'none');
    $custom_upload.css('display', 'flex');
    $preview_img.attr('src', '#');
    $real_upload_btn.val(null);
  });
})