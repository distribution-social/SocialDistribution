import { extractUUID } from "./utility.js";
import { makeAjaxCall, makeAjaxCallAsync } from "./ajax.js";
//post card scripts

export function getPostLikes(post){
  const uuid = extractUUID(post.id)
  const like_count = $(`#like-count-${uuid}`)
  const like_url = `${post.id}/likes`
  makeAjaxCallAsync(like_url,'GET',null,{Authorization: 'Basic '+post.auth_token},
  function (response,status){
    const count = response.items.length
    like_count.html(count);
  },
  function (error,status){
    console.log(error)
  })
}

export function getComments(post){
  const uuid = extractUUID(post.id)
  const comments = $(`#collapse_${uuid}`)
  const comment_url = `${post.id}/comments?page=1&size=10`
  makeAjaxCallAsync(comment_url,'GET',null,{Authorization: 'Basic '+post.auth_token},
  function (response,status){
    $.each(response.comments, function(index,comment){
      const commentData = {
        ...comment
      }
      let headers = {
        'X-CSRFToken': '{{ csrf_token }}'
      }
      makeAjaxCallAsync('/comment.html','POST',JSON.stringify(commentData),headers,
      function (response,status){
        let new_com = document.createElement('div');
        new_com.classList.add('card-footer');
        new_com.innerHTML = response
        comments.append(new_com)
      },
      function (error,status){
        console.log(error)
      })
    })
  },
  function (error,status){
    console.log(error)
  })
}

export function addPostLikeEventListener(post,author){

  const data = {
    type: 'like',
    author,
    summary: `${author.displayName} liked your post`,
    object: post.id
  }

  const uuid = extractUUID(post.id)
  $(`#like-post-${uuid}`).click(function(e) {
      e.preventDefault();
      const url = `${post.author.url}/inbox`
      $.ajax({
          type: 'POST',
          url: url,
          data: JSON.stringify(data),
          contentType: 'application/json',
          headers: {
            Authorization: 'Basic '+post.auth_token,
          },
          // xhrFields: {
          //   withCredentials: true
          // },
          success: function (result, statusText, xhr) {
            showAndDismissAlert("info",result)
            if(xhr.status == 201 || xhr.status == 200){
              let value = parseInt($(`#like-count-${uuid}`).html());
              value++;
              $(`#like-count-${uuid}`).html(value);
            }

            showAndDismissAlert("info", result)

          },
          error: function (xhr, exception) {
            let error_message = '';
            if (xhr.status === 0) {
              error_message = 'No connection to server. Check Network.';
            } else if (xhr.status == 404) {
              error_message = 'Requested page not found. [404]';
            } else if (xhr.status == 500) {
              error_message = 'Internal Server Error [500].';
            } else if (exception === 'timeout') {
              error_message = 'Timed out. Try again.';
            } else if (exception === 'abort') {
              error_message = 'Request aborted.';
            } else {
              error_message = 'Could not make request. ' + xhr.responseText;
            }
            showAndDismissAlert("error",error_message)
          }
      });
  }
  )
}

export function addCommentLikeEventListener(comment,author){
  const uuid = extractUUID(comment.id)
  $(`#like-comment-${uuid}`).click(function(e) {
      e.preventDefault();
      const url = `${comment.author.url}/inbox`
      $.ajax({
          type: 'POST',
          url: url,
          data: {
              type: 'like',
              author: author,
              summary: `${author.displayName} liked your comment`,
              object: comment.id
          },
          headers: {
            Authorization: 'Basic '+comment.auth_token
          },
          // xhrFields: {
          //   withCredentials: true
          // },
          success: function (result, statusText, xhr) {
            showAndDismissAlert("info",result)
            // console.log(result)
            if(xhr.status == 201 || xhr.status == 200){
              let value = parseInt($(`#like-count-${uuid}`).html());
              value++;
              $(`#like-count-${uuid}`).html(value);
            }

            showAndDismissAlert("info", result)

          },
          error: function (xhr, exception) {
            let error_message = '';
            if (xhr.status === 0) {
              error_message = 'No connection to server. Check Network.';
            } else if (xhr.status == 404) {
              error_message = 'Requested page not found. [404]';
            } else if (xhr.status == 500) {
              error_message = 'Internal Server Error [500].';
            } else if (exception === 'timeout') {
              error_message = 'Timed out. Try again.';
            } else if (exception === 'abort') {
              error_message = 'Request aborted.';
            } else {
              error_message = 'Could not make request. ' + xhr.responseText;
            }
            showAndDismissAlert("error",error_message)
          }
      });
  }
  )
}

export function addDeletePostListener(uuid){
    // console.log(uuid)
  $(`#delete-post-${uuid}`).on('click', function(event) {
    // console.log("Like button clicked")
    event.preventDefault();
    const url = `delete-post/${uuid}/`
    var postId = $(this).attr('id').replace('delete-post-', '');
    $(`#delete-post-modal-${uuid}`).modal('show');
    $(`#confirm-delete-post-${uuid}`).on('click', function(event) {
      event.preventDefault();
      $.ajax({
            type: 'POST',
            url:url,
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                action: 'delete_post'
            },
            // xhrFields: {
            //   withCredentials: true
            // },
            success: function (result) {

              $(`#delete-post-modal-${uuid}`).hide()
              showAndDismissAlert("info","Post successfully deleted!");
              setTimeout(function(){
                location.reload();
              },500);
            },
            error: function (xhr, exception) {
              let error_message = '';
              if (xhr.status === 0) {
                error_message = 'No connection to server. Check Network.';
              } else if (xhr.status == 404) {
                error_message = 'Requested page not found. [404]';
              } else if (xhr.status == 500) {
                error_message = 'Internal Server Error [500].';
              } else if (exception === 'timeout') {
                error_message = 'Timed out. Try again.';
              } else if (exception === 'abort') {
                error_message = 'Request aborted.';
              } else {
                error_message = 'Could not make request. ' + xhr.responseText;
              }
              showAndDismissAlert("error",error_message)
            }
        });
      $(`#confirm-delete-post-${uuid}`).modal('hide');
    });
  });
}



// function addCommentHandler(event, comment){
//   // add submit event listener to comment form
//     // prevent default form submission
//     event.preventDefault();
//     console.log(comment)
//     // console.log(post)

//     // serialize form data
//     // var formData = $(this).serialize();

//     // // send AJAX request to submit form data
//     // $.ajax({
//     //   type: "POST",
//     //   url: $(this).attr("action"),
//     //   data: formData,
//     //   success: function(response) {
//     //     // update comment section with AJAX response
//     //     $("#comment-section").html(response);
//     //   },
//     //   error: function(xhr, status, error) {
//     //     // handle AJAX error
//     //     console.error(xhr);
//     //   }
//     // });
// };