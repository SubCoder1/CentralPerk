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

// JS code for uploaded file-name to appear on custom-btn
const realfilebtn = document.getElementById("real-file");
const custombtn = document.getElementById("img-btn-custom");

if (realfilebtn && custombtn) {
  custombtn.addEventListener("click", function() {
    realfilebtn.click();
  });
  
  realfilebtn.addEventListener("change", function() {
    if (realfilebtn.value) {
      custombtn.value = realfilebtn.value;
    } else {
      custombtn.value = "No files selected";
    }
  });
};

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
  