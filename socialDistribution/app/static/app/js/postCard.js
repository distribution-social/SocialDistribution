
//post card scripts

export function addLikeEventListener(uuid){
    // console.log(uuid)
    $(`#like-post-${uuid}`).click(function(e) {
        e.preventDefault();
        const url = `/posts/${uuid}/like`
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                action: 'add_like_post'
            },
            success: function (result) {
              showAndDismissAlert("info",result)
              // console.log(result)
              if(result.toLowerCase() === "liked"){
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