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
                var promises = [];
                promises.push(
                    $.ajax({
                        url: '/post_card.html',
                        type: 'POST',
                        data: JSON.stringify(postData),
                        contentType: 'application/json',
                        headers: headers
                    }))
            Promise.all(promises).then(function(datas){
                for(var y = 0; y < datas.length; y++){
                        // Append the new item to the list
                        $('#post-stream').append(datas[y]);
                        spinner.style.display = 'none';
                        addPostLikeEventListener(postData,current_author)
                        addDeletePostListener(postData.uuid)
                }
            });
            });
        }
        spinner.style.display = 'none';
    },
    function (error,status){
        console.log(error)
    });
});
