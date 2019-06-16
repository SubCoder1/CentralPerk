// JS code to set height of comment-view-card-body(comment box in view_post)
const card_height = parseInt(document.getElementById('id_view-post-card').clientHeight);
const card_header_height = parseInt(document.getElementById('id_view-post-card-header').clientHeight);
const card_footer_height = 53;

var value = card_height - (card_header_height + card_footer_height) - 10;
var attribute = "height:" + value.toString() + "px";
//console.log(attribute);

var comment_body_height = document.getElementById('id_view-post-comment-body');
comment_body_height.setAttribute('style', attribute);


//JS code for handling comment replies
var length = 0;
var replies = document.querySelectorAll('.comment-reply');
replies.forEach(function(reply){
    reply.addEventListener("click", function() {
        document.querySelector(".reply-to").value = reply.id;
        var value = "@" + reply.parentElement.querySelector('.m-0').getElementsByTagName('a')[0].innerText + "";
        document.getElementById('comment_box').value = value;
        length = value.length;
        document.getElementById('comment_box').focus();
    });
});

var comment_textbox = document.getElementById('comment_box');
comment_textbox.addEventListener('input', function() {
    if (comment_textbox.value.length < length-1) {
        document.querySelector(".reply-to").value = "";
    }
    else if (comment_textbox.value == "") {
        document.querySelector(".reply-to").value = "";
    }
});