import { makeAjaxCallAsync } from "./ajax.js";
import { addPostLikeEventListener, addDeletePostListener, getComments, getPostLikes } from "./postCard.js"
import { extractUUID } from "./utility.js";

const myDataElement = document.getElementById('my-data');
const post = JSON.parse(myDataElement.dataset.myData);
const myAuthorElement = document.getElementById('my-author');
let current_author = null
try{
    current_author = JSON.parse(myAuthorElement.dataset.myAuthor);
}
catch{
    current_author = null;
}
$(document).ready(function() {
    getPostLikes(post);
    getComments(post,current_author);
    if(current_author != null){
        addPostLikeEventListener(post,current_author)
        addDeletePostListener(post.uuid)
    }
})