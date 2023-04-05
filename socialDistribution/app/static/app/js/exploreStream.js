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
$(document).ready(async function() {
    // console.log('{{ csrf_token|length }}');

    spinner.style.display = 'block';
    var headers = {
        'X-CSRFToken': '{{ csrf_token }}'
    }
    makeAjaxCallAsync("/public_authors","GET",null,headers,
    function (response,status){
        $.each(response.authors, function(index,author){
            makeAjaxCallAsync(`${author.id}/posts`,'GET',null,{Authorization: 'Basic '+author.auth_token},
            function(response,status){
                const posts = response.items.filter(item => item.visibility === "PUBLIC" && !Boolean(item.unlisted));
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
                    async function(response,status){
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
                    
                        await getPostLikes(postData);
                        await getComments(postData);
                        if(current_author != null){
                            addPostLikeEventListener(postData,current_author)
                            addDeletePostListener(postData.uuid)
                        }

                        spinner.style.display = 'none';

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


