import { addPostLikeEventListener, addDeletePostListener } from "./postCard.js"
import { extractUUID } from "./utility.js";
import { makeAjaxCall, makeAjaxCallAsync } from "./ajax.js";

const myAuthorElement = document.getElementById('my-author');
const current_author = myAuthorElement.dataset.myAuthor;

const spinner = document.getElementById("spinner2")
// fetches the post when document loads.
$(document).ready(function() {
    // console.log('{{ csrf_token|length }}');

    spinner.style.display = 'block';
    var headers = {
        'X-CSRFToken': '{{ csrf_token }}'
    }
    makeAjaxCallAsync("/home_posts","GET",null,headers,
    function (response,status){

        if(response.trim() == ''){
            $('#post-stream').html('No posts to show, use the \'Explore\' tab to find people to follow.')
        }else{
            $('#post-stream').html(response);
        }
        spinner.style.display = 'none';
    },
    function (error,status){
        console.log(error)
    });
});
