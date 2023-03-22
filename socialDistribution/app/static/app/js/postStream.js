import { addLikeEventListener, addDeletePostListener } from "./postCard.js"
import { extractUUID } from "./utility.js";
const spinner = document.getElementById("spinner2")
// fetches the post when document loads.
$(document).ready(function() {
    console.log('{{ csrf_token|length }}');
    
   
    spinner.style.display = 'block'; 

    $.ajax({
        url: "/posts",
        type: 'GET',
        success: function(res) {
            $.each(res.posts, function(index, post) {
                const postData = {
                    uuid: extractUUID(post.id),
                    ...post
                }


                postData.author.id = extractUUID(post.author.id)
                postData.likeCount = 5; // hardcoding for now, since we dont give 
                console.log(postData)

                $.ajax({
                    url: '/post_card.html',
                    type: 'POST',
                    data: JSON.stringify(postData),
                    contentType: 'application/json',
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}'
                    },
                    success: function(template) {
                        console.log(template)
                  
                        $('#post-stream').append(template);
                        spinner.style.display = 'none'; 
                        addLikeEventListener(postData.uuid)
                        addDeletePostListener(postData.uuid)
                       
              
                    },
                    error: function(xhr, status, error) {
                        console.error(xhr.responseText);
                    }
                });
    
            });
            $('#post-stream').removeClass('d-none');
        },
        error: function(xhr, status, error) {
            console.error(xhr.responseText);
        }
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