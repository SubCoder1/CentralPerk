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

  // Bookmark posts on-click effect
  var $post_bookmark = $('.lnr-bookmark');
  $post_bookmark.on('click', function() {
    if ($post_bookmark.hasClass('bookmarked')) {
      $post_bookmark.removeClass('bookmarked');
    } else {
      $post_bookmark.toggleClass('bookmarked');
    }
  });

  // JS code for slide-in-as-you-scroll-down-post-cards
  (function($) {
    $.fn.visible = function(partial) {
      
        var $t            = $(this),
            $w            = $(window),
            viewTop       = $w.scrollTop(),
            viewBottom    = viewTop + $w.height(),
            _top          = $t.offset().top,
            _bottom       = _top + $t.height(),
            compareTop    = partial === true ? _bottom : _top,
            compareBottom = partial === true ? _top : _bottom;
      
      return ((compareBottom <= viewBottom) && (compareTop >= viewTop));
    };
  })(jQuery);

  var win = $(window);
  function post_card_stack_up() {
    var allMods = $(".index-post-card");

    // Already visible post-cards
    allMods.each(function(i, el) {
      var el = $(el);
      if (el.visible(true)) {
        el.addClass("already-visible"); 
      } 
    });

    win.scroll(function(event) {

      allMods.each(function(i, el) {
        var el = $(el);
        if (el.visible(true) && !el.hasClass("already-visible")) {
          el.addClass("come-in"); 
        } 
      });
      
    });
  }

  post_card_stack_up();

  // JS code for post-card data overflow management
  function manage_status_caption() {
    var $post_container = $('.index-post-card-body, .prof-post-card-body');
    var $elms = $post_container.children('#post-data');
    $.each($post_container, function (index, value) {
        var post = $elms[index].textContent.replace(/"/g, "");
        var newline_count = (post.match(/\\r\\n/g) || '').length + 1;
          if (newline_count) {
            var lines = post.split("\\r\\n");
            if (lines.length > 5) {
              var read_less = lines.slice(0,5);
              for (var j=0; j < 5; j++) {
                $post_container[index].innerHTML += read_less[j] + '<br/>';
              }
              var read_more = $post_container[index].getElementsByTagName("a")[0];
              if (read_more) {
                $post_container[index].removeChild(read_more);
                var read_more_link = '<a class="body_link read-more" href="' + read_more + '">Read more. . .</a>'
                $post_container[index].innerHTML += read_more_link;
              } else {
                $post_container[index].innerHTML += ". . . .";
              }
            } else {
              var read_less = lines.slice(0,lines.length);
              for (var j=0; j < lines.length; j++) {
                $post_container[index].innerHTML += read_less[j] + '<br/>';
              }
            }
          } else {
            $post_container[index].innerHTML += post;
          }
    });
  }

  manage_status_caption();

  $('.post-container').on('contentchanged', function() {
    manage_status_caption();
    post_card_stack_up();
  })

  // JQuery code to preview uploaded image and clear it (if clicked on img)
  var $real_upload_btn = $('#real-file');
  var $custom_upload = $('#img-btn-custom');
  var $preview_img = $('#preview-img');

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