// JS code for nav-bar search scroll-effect
var prevScrollpos = window.pageYOffset;
window.onscroll = function() {
var currentScrollPos = window.pageYOffset;
  if (prevScrollpos > currentScrollPos) {
    document.getElementById("search").style.top = "0";
  } else {
    document.getElementById("search").style.top = "-100px";
  }
  prevScrollpos = currentScrollPos;
}

// JS code for post-card data overflow management
var elms = document.querySelectorAll("[id='post-data']");
var post_container = document.querySelectorAll("[id='post-container']");
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
        post_container[i].innerHTML += "<a class='body_link' href='#' style='text-decoration: none'>Read More..</a>"
      } else {
        var read_less = lines.slice(0,lines.length);
        for (var j=0; j < lines.length; j++) {
          post_container[i].innerHTML += read_less[j] + '<br/>';
        }
      }
    } else if (post.length > 200) {
      post_container[i].innerHTML += post.slice(0,200);
      post_container[i].innerHTML += "<a class='body_link' href='#' style='text-decoration: none'>Read More..</a>"
    } 
    else {
      post_container[i].innerHTML += post;
    }
  }).call(this, i);
}
  