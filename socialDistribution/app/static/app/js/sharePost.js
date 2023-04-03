function sharePost(post) {
    // Get the form element
    // remove bad control characters

    let cleanedJsonStr = post.replace(/[\x00-\x1F\x7F-\x9F]/g, '');

    let parsedPost = JSON.parse(cleanedJsonStr)
    var form = document.getElementById(`share-form-${parsedPost.uuid}`);

    // Get all selected followers
    var selectedFollowers = [];
    var checkboxes = form.elements['follower'];
    var pendingRequests = 0;
    const data = {
      ...parsedPost,

    }

    for (var i = 0; i < checkboxes.length; i++) {
      if (checkboxes[i].checked) {
        // selectedFollowers.push(checkboxes[i].value);
        // const followerUrl = checkboxes[i].value + "/inbox"
        followerObj = JSON.parse(checkboxes[i].value)
        url = followerObj.url + "/inbox"

        // url = 'http://127.0.0.1:8000/api/authors/78bc8cfc-58c5-442c-a668-966eaded48fd/inbox'


        pendingRequests++
        $.ajax({
          type: 'POST',
          url: url,
          data: JSON.stringify(data),
          headers: {
            "Authorization": 'Basic '+followerObj.auth_token,
          "Content-Type": 'application/json; charset=utf-8'
          },
          xhrFields: {
            withCredentials: true
          },
          success: function (result) {
           pendingRequests--
           checkPendingRequests()
          },
          error: function (xhr, exception) {
            pendingRequests--
            checkPendingRequests()
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
    }

    function checkPendingRequests(){
      if (pendingRequests == 0){
        $(`#share-post-modal-${parsedPost.uuid}`).modal('hide');
        alert("Has been shared")

      }

    }


    // Do something with the selected followers
    console.log(selectedFollowers);
}