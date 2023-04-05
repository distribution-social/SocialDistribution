import { addPostLikeEventListener, addDeletePostListener, getPostLikes, getComments } from "./postCard.js"
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
    makeAjaxCallAsync("/home_authors","GET",null,headers,
    function (response,status){
        $.each(response.authors, function(index,author){
            makeAjaxCallAsync(`${author.id}/posts`,'GET',null,{Authorization: 'Basic '+author.auth_token},
            function(response,status){
                spinner.style.display = 'none';
                const types = ["PUBLIC","FRIENDS"]
                const posts = response.items.filter(item => types.includes(item.visibility));
                $.each(posts, function(index, post) {
                    // console.log(post)
                    const postData = {
                        uuid: extractUUID(post.id),
                        auth_token: author.auth_token,
                        tag: author.tag,
                        ...post
                    }
                    postData.author.id = extractUUID(post.author.id)
                    makeAjaxCallAsync('/post_card.html','POST',JSON.stringify(postData),headers,
                    function(response,status){
                        // console.log(`<div data-sort=${postData['published']}>${response}</div>`)
                        $('#post-stream').append(`<div style="width: 100%" data-sort=${postData['published']}>${response}</div>`)
                        .children()
                        // sort the object collection based on data-sort value
                        .sort(function(a, b) {
                          // get difference for sorting based on number
                          let first = new Date($(a).data('sort'))
                          let sec = new Date($(b).data('sort'))
                          return sec - first;
                          // append back to parent for updating order
                        }).appendTo('#post-stream');
                        spinner.style.display = 'none';
                        getPostLikes(postData);
                        getComments(postData);
                        if(current_author != null){
                            addPostLikeEventListener(postData,current_author)
                            addDeletePostListener(postData.uuid)
                        }

                    },
                    function (error,status){
                        console.log(error)
                    })
                });

            },
            function(error,status){
                console.log(error);
            })
        })


    },
    function (error,status){
        console.log(error)
    });
});
