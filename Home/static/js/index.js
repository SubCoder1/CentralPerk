$(document).ready(function() {
  // JS code for navbar on-scrolldown animation
  var navbar = document.getElementById("navbar");
  var $navbar = $('#navbar');
  window.onscroll = function() {
    if ($navbar.css('padding') != '10px') {
      scrollFunction();
    }
  };
  var logo = document.getElementById("logo");
  var $brand_ico = $('#brand-ico');

  function scrollFunction() {
      if (document.body.scrollTop > 30 || document.documentElement.scrollTop > 30) {
        logo.style.fontSize = "20px";
        $brand_ico.css('height', '38px');
      } else {
        logo.style.fontSize = "25px";
        $brand_ico.css('height', '32px');
      }
  }

  // Welcome msg close animation
  var $close_btn = $('.close');
  $close_btn.on('click', function() {
    if ($(this).parent().parent().hasClass('welcome-card')) {
      $(this).parent().parent().hide('slow', function(){ $(this).remove(); });
    }
  });

  // Bookmark posts on-click effect
  var $post_bookmark = $('.lnr-bookmark');
  $post_bookmark.on('click', function(){
    if ($(this).hasClass('bookmark-saved')) {
      $(this).removeClass('bookmark-saved');
    } else {
      $(this).toggleClass('bookmark-saved');
    }
  });

  // Hide new-notification till new notifications pushes-in via socket
  var $new_notif_indicator = $('.new-notif-indicator');
  var $notif_btn = $('.notif-btn');
  var $notif_modal = $('#notification');
  $notif_btn.on('click', function() {
    if ($notif_btn.hasClass('updated') == false) {
      // This piece of code adds a flag to ensure that notif only gets updated from server side
      $notif_btn.addClass('updated');
    }
    $new_notif_indicator.css('background', 'transparent');
  });
  // This code resolves the bug in which new-notif-indicator is shown even after notif-btn is clicked.
  // although, this happens only on the 1st time but still is annoying af! B|
  $notif_modal.on('hidden.bs.modal', function (e) {
    $new_notif_indicator.css('background', 'transparent');
  });

  // Hide new-msg-indicator till new msgs pushes-in via socket
  var $new_msg_indicator = $('.new-msg-indicator');
  var $p_chat_btn = $('.chat-btn');
  var $p_chat_modal = $('#p-chat');
  $p_chat_btn.on('click', function() {
    $new_msg_indicator.css('background', 'transparent');
  });
  // This code resolves bug where p-chat-cover is open and indicator is shown in background
  // (maybe because new chat can push via socket & as user hasn't open any specific p-chat)
  $p_chat_modal.on('hidden.bs.modal', function (e) {
    $new_msg_indicator.css('background', 'transparent');
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

  $('.post-container').on('contentchanged', function() {
    post_card_stack_up();
  })

  // JQuery code to preview uploaded image and clear it (if clicked on img)
  var $real_upload_btn = $('#real-file');
  var $custom_upload = $('#img-btn-custom');
  var $preview_img_container = $('.preview-img-container');
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
    var $upload_file = $(this).val();
    if ($upload_file != '') {
      var idxDot = $upload_file.lastIndexOf(".") + 1;
      var extFile = $upload_file.substr(idxDot, $upload_file.length).toLowerCase();
      if (extFile=="jpg" || extFile=="jpeg" || extFile=="png") {
        $custom_upload.css('display', 'none');
        $preview_img_container.css('border', '5px solid #161515');
        previewPIC(this);
      } else {
        $preview_img_container.css('border', '5px solid orangered');
      }
    }
  });

  $preview_img.on('click', function() {
    $preview_img.css('display', 'none');
    $custom_upload.css('display', 'flex');
    $preview_img.attr('src', '#');
    $real_upload_btn.val(null);
  });

  // show loading.gif on modal close
  var $p_chat_modal = $('#p-chat');
  var $p_chat_cover_wrapper = $('.p-chat-cover-wrapper');
  $p_chat_modal.on('hidden.bs.modal', function (e) {
    if ($p_chat_cover_wrapper.children().hasClass('wrap-msg-list-res')) {
      $p_chat_cover_wrapper.html("<img class='modal-loading-gif loading-gif-active' src='/static/img/loading.gif'/>");
    }
  });
})