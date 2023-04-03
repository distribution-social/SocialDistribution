import { addPostLikeEventListener, addDeletePostListener, getPostLikes } from "./postCard.js"
import { extractUUID } from "./utility.js";
import { makeAjaxCall, makeAjaxCallAsync } from "./ajax.js";

const myAuthorElement = document.getElementById('my-author');
let current_author = null
try{
    current_author = JSON.parse(myAuthorElement.dataset.myAuthor);
}
catch{
    current_author = null;
}

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
        spinner.style.display = 'none';
        if(response.posts.length == 0){
            $('#post-stream').html('No posts to show, use the \'Explore\' tab to find people to follow.')
        }else{
            $.each(response.posts, function(index, post) {
                // console.log(post)
                const postData = {
                    uuid: extractUUID(post.id),
                    ...post
                }
                postData.author.id = extractUUID(post.author.id)
                makeAjaxCallAsync('/post_card.html','POST',JSON.stringify(postData),headers,
                function(response,status){
                    $('#post-stream').append(response);
                    spinner.style.display = 'none';
                    getPostLikes(postData)
                    if(current_author != null){
                        addPostLikeEventListener(postData,current_author)
                        addDeletePostListener(postData.uuid)
                    }
                },
                function (error,status){
                    console.log(error)
                })
            });
        }
    },
    function (error,status){
        console.log(error)
    });
});
