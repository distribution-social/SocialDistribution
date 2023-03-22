import { addLikeEventListener, addDeletePostListener } from "./postCard.js"
import { extractUUID } from "./utility.js";

const myDataElement = document.getElementById('my-data');
const postUUID = myDataElement.dataset.myData;
const spinner = document.getElementById("spinner3")
$(document).ready(function() {
    $(`#collapse_${postUUID}`).show()
    console.log("IN POST_DETAILS.js")
        
   
    spinner.style.display = 'display'; 
    $.ajax({
        url: "/post-details",
        type: 'GET',
        data: {uuid: postUUID},
        success: function(res) {
            const postData = {
                uuid: extractUUID(res.post.id),
                ...res.post
            }
            postData.author.id = extractUUID(res.post.author.id)

            console.log(res)

            $.ajax({
                url: '/post_detail.html',
                type: 'POST',
                data: JSON.stringify(postData),
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                success: function(template) {
                    console.log(template)
            
                    $('#post-detail').append(template);
                    spinner.style.display = 'none'; 
                    addLikeEventListener(postData.uuid)
                    addDeletePostListener(postData.uuid)
          
                },
                error: function(xhr, status, error) {
                    console.error(xhr.responseText);
                }
            });
        },
        error: function(xhr, status, error) {
            console.error(xhr.responseText);
        }
    });
})