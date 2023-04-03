import { addPostLikeEventListener, addDeletePostListener } from "./postCard.js"
import { extractUUID } from "./utility.js";

const myDataElement = document.getElementById('my-data');
const post = myDataElement.dataset.myData;

const myAuthorElement = document.getElementById('my-author');
const current_author = myAuthorElement.dataset.myAuthor;
// console.log(current_author)
const spinner = document.getElementById("spinner3")
$(document).ready(function() {
    $(`#collapse_${postUUID}`).show()

    spinner.style.display = 'display';
    data = {
        id: post.id
    }

    makeAjaxCallAsync("/post_details","GET",data,headers,
    function (response,status){
        $('#post-detail').html(response);
        spinner.style.display = 'none';
    },
    function (error,status){
        console.log(error)
    });
    // $.ajax({
    //     url: "/post-details",
    //     type: 'GET',
    //     data: {uuid: postUUID},
    //     success: function(res) {
    //         console.log(res)
    //         const postData = {
    //             uuid: extractUUID(res.post.id),
    //             ...res.post
    //         }
    //         postData.author.id = extractUUID(res.post.author.id)

    //         $.ajax({
    //             url: '/post_detail.html',
    //             type: 'POST',
    //             data: JSON.stringify(postData),
    //             contentType: 'application/json',
    //             headers: {
    //                 'X-CSRFToken': '{{ csrf_token }}'
    //             },
    //             success: function(template) {
    //                 $('#post-detail').append(template);
    //                 spinner.style.display = 'none';
    //                 addPostLikeEventListener(postData,current_author)
    //                 addDeletePostListener(postData.uuid)

    //             },
    //             error: function(xhr, status, error) {
    //                 console.error(xhr.responseText);
    //             }
    //         });
    //     },
    //     error: function(xhr, status, error) {
    //         console.error(xhr.responseText);
    //     }
    // });
})