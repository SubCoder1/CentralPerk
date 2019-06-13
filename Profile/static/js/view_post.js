// JS code to set height of comment-view-card-body(comment box in view_post)
const card_height = parseInt(document.getElementById('id_view-post-card').clientHeight);
const card_header_height = parseInt(document.getElementById('id_view-post-card-header').clientHeight);
const card_footer_height = 53;

var value = card_height - (card_header_height + card_footer_height) - 10;
var attribute = "height:" + value.toString() + "px";
console.log(attribute);

var comment_body_height = document.getElementById('id_view-post-comment-body');
comment_body_height.setAttribute('style', attribute);
