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
    makeAjaxCallAsync("/public_posts","GET",null,headers,
    function (response,status){
        spinner.style.display = 'none';
        if(response.posts.length == 0){
            $('#post-stream').html('No posts to show.')
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
        }

    },
    function (error,status){
        console.log(error)
    });
});





//TODO: THE FOLLOWING ADD LIKE COMMENT, ADD IT AS A LISTENER ON THE BUTTON WHEN WE HAVE COMMENT LIKE INFO.

// $(document).ready(function() {
//   $("#like-comment-{{comment.uuid}}").click(function(e) {
//       e.preventDefault();

//       $.ajax({
//           type: 'POST',
//           url: '{% url "add_like_comment" post_id=post.uuid comment_id=comment.uuid %}',
//           data: {
//               csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
//               action: 'add_like_comment'
//           },
//           success: function (result) {
//             showAndDismissAlert("info",result)
//             if(result == "Liked"){
//               let value = parseInt($("#like-count-{{comment.uuid}}").html());
//               value++;
//               $("#like-count-{{comment.uuid}}").html(value);
//             }
//           },
//           error: function (xhr, exception) {
//             let error_message = '';
//             if (xhr.status === 0) {
//               error_message = 'No connection to server. Check Network.';
//             } else if (xhr.status == 404) {
//               error_message = 'Requested page not found. [404]';
//             } else if (xhr.status == 500) {
//               error_message = 'Internal Server Error [500].';
//             } else if (exception === 'timeout') {
//               error_message = 'Timed out. Try again.';
//             } else if (exception === 'abort') {
//               error_message = 'Request aborted.';
//             } else {
//               error_message = 'Could not make request. ' + xhr.responseText;
//             }
//             showAndDismissAlert("error",error_message)
//           }
//       });
//   }
//   )
// })


