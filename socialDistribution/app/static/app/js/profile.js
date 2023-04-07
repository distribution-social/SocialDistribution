// References:
//  https://css-tricks.com/crafting-reusable-html-templates/
//  https://dmitripavlutin.com/parse-url-javascript/
//  https://stackoverflow.com/questions/3216013/get-the-last-item-in-an-array
//  https://www.w3schools.com/jsref/prop_element_childelementcount.asp

import { addPostLikeEventListener, addDeletePostListener, getPostLikes, getComments } from "./postCard.js"
import { extractUUID, uuidToHex } from "./utility.js";
import { getGitHubUsername, fetchActivitiesJSON, createHTMLCard } from "./github.js";
import { makeAjaxCall, makeAjaxCallAsync } from "./ajax.js";
const spinner = document.getElementById("spinner2")
const myAuthorElement = document.getElementById('my-author');
let current_author = null
try{
    current_author = JSON.parse(myAuthorElement.dataset.myAuthor);
}
catch{
    current_author = null;
}

$(document).ready(function() {

    getAndSetProfileCard();
    //setFollowing(serialized_followings, user_id, author_id, author_host);

    // get followers from server and use data to set followers and true friends
    var followersUrl;
    if (author_host.includes("p2psd")) {
        followersUrl = new URL("authors/" + author_id + "/followers/", author_host);
    } else if (author_host.includes("bigger-yoshi")){
        followersUrl = new URL("authors/" + author_id + "/followers", author_host);
    } else {
        followersUrl = new URL("authors/" + uuidToHex(author_id) + "/followers", author_host);
    }

    fetch(followersUrl, {method: "GET", redirect: "follow", headers: auth_headers}).then((response) => {
        if (response.status === 200) { // OK
            return response.json();
        } else {
            alert("Something went wrong: " + response.status);
        }
    }).then((data) => {
        const followers = data.items;
        setFollowers(followers, user_id, author_id, author_host, nickname_table);
        setFriends(followers, author_id);
        return;
    })

});

function getAndSetProfileCard() {
    var authorProfileUrl;
    if (author_host.includes("p2psd")) {
        authorProfileUrl = new URL("authors/" + author_id + "/", author_host);
    } else if (author_host.includes("bigger-yoshi")){
        authorProfileUrl = new URL("authors/" + author_id, author_host);
    } else {
        authorProfileUrl = new URL("authors/" + uuidToHex(author_id), author_host);
    }

    // set profile card info
    fetch(authorProfileUrl, {method: "GET", redirect: "follow", headers: auth_headers}).then((response) => {
        if (response.status === 200) { // OK
            return response.json();
        } else {
            alert("Something went wrong: " + response.status);
        }
    }).then((data) => {
        document.title = `Profile (${data.displayName})`;
        let profileCard = document.getElementById("profile_card");
        if (data.profileImage !== null && data.profileImage !== "") {$(profileCard).find(".profile_image").attr("src", data.profileImage);}
        $(profileCard).find(".profile_github").attr("href", data.github);
        $(profileCard).find(".profile_display_name").text(data.displayName);
        $("#edit_profile_from").attr("action","/authors/"+author_id+"/edit");

        try{
            var github_username = getGitHubUsername(data.github);
            if (github_username) {
                fetchActivitiesJSON(github_username).then(activities => {
                const target = document.getElementById("github_activity_stream");
                for (var activity of activities) {
                let html_element = createHTMLCard(activity.id, activity.link, activity.title, activity.published, activity.updated, activity.authors);
                target.innerHTML += html_element;
                }
            });
            } else {
                const target = document.getElementById("github_activity_stream");
                target.innerHTML += `GitHub information for <b>${data.displayName}</b> is not available`;
            }
    
        }
        catch {
            console.log('Issue with github.')
        }
        let headers = {
            'X-CSRFToken': '{{ csrf_token }}'
        }
        makeAjaxCallAsync(`/profile_authors/${author_id}`,"GET",null,headers,
        function (response,status){
            $.each(response.authors, function(index,author){
                makeAjaxCallAsync(`${author.id}/posts`,'GET',null,{Authorization: 'Basic '+author.auth_token},
                function(response,status){
                    spinner.style.display = 'none';
                    const types = ["PUBLIC"]
                    const posts = response.items.filter(item => types.includes(item.visibility)&& !Boolean(item.unlisted));
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
                            getComments(postData,current_author);
                            if(current_author != null){
                                addPostLikeEventListener(postData,current_author)
                                addDeletePostListener(postData.uuid)
                            }

                        },
                        function (error,status){
                            // console.log(error)
                        })
                    });

                },
                function(error,status){
                    // console.log(error);
                })
            })

        },
        function (error,status){
            // console.log(error)
        });
        return;
    })
    // handle follow unfollow button
    let authorIsFollowingUrl;
    if (author_host.includes("p2psd")) {
        authorIsFollowingUrl = new URL("authors/" + author_id + "/followers/" + user_id + "/", author_host);
    } else if (author_host.includes("bigger-yoshi")){
        authorIsFollowingUrl = new URL("authors/" + author_id + "/followers/https://www.distribution.social/api/authors/" + user_id, author_host);
        // console.log("|||||||||||||||||||||", authorIsFollowingUrl);
    } else {
        authorIsFollowingUrl = new URL("authors/" + uuidToHex(author_id) + "/followers/" + user_id, author_host);
    }

    const authorIsPendingURL = new URL("get-is-pending/" + author_id, `${window.location.protocol}//` + window.location.host);

    fetch(authorIsPendingURL, {method: "GET", redirect: "follow", headers: local_auth_headers}).then(response => {
        return response.json()
    }).then(data => {
       var is_pending = data.is_pending;
    //    console.log(is_pending);
  

    fetch(authorIsFollowingUrl, {method: "GET", redirect: "follow", headers: auth_headers}).then((response) => {

        if (response.status === 200) { // OK
            let temp = response.json();
            return temp;
        } else if (response.status === 404) {
            return JSON.parse('{"is_following" : "false"}');
        } else {
            alert("Something went wrong: " + response.statusText);
        }
    }).then((data) => {
        let is_following;
        if (data.is_following != null && String(data.is_following).toLowerCase() === "true"){
            is_following = true;
        }
        else if (data.accepted != null && String(data.accepted).toLowerCase() === "true"){
            is_following = true;
        }
        else if (data.approved != null && data.approved === true){
            console.log(authorIsFollowingUrl);
            console.log("Here!!!!")
            is_following = true;
        }
        else if (data.found != null && data.found === true){
            is_following = true;
        }

        else {
            is_following = false;
        }
        if (is_following) {
            $("#follow_unfollow_button").attr('disabled', true).text("Following");

            if (author_host.includes("bigger-yoshi")){
                fetch(authorProfileUrl, {method: "GET", redirect: "follow", headers: auth_headers}).then((response) => {
            if (response.status === 200) { // OK
                return response.json();
            } else {
                alert("Something went wrong: " + response.status);
            }
            }).then((data) => {

                const addToFollowingURL = new URL("add-to-following", `${window.location.protocol}//` + window.location.host);

                const foreignAuthorObject = {user_id: user_id, author_id: author_id, foreign_user_object: data};

                fetch(addToFollowingURL, {
                    method: "POST",
                    redirect: "follow",
                    headers: new Headers({
                    'Authorization': 'Basic '+btoa('server1:123'),
                    'Content-Type': 'application/json'
                }),
                    body: JSON.stringify(foreignAuthorObject)
                });
            })
        }

        } 
        else if (is_pending){
            console.log("IS_PENDING---------------")
            $("#follow_unfollow_button").attr('disabled', true).text("Pending Follow Request");
        }
        
        else {
            $("#follow_unfollow_button").text("Request to Follow");

            const element = document.getElementById("follow_unfollow_button");
            if (element) {
                element.addEventListener("click", sendFollowRequestToInbox);
            }

        }
    });
  });

}


function sendFollowRequestToInbox(e){

        e.preventDefault();

        const element = document.getElementById("follow_unfollow_button");

        element.innerText = "Pending Follow Request";

        element.setAttribute('disabled', '');

        getSingleAuthorInfo(user_url, local_auth_headers).then(currentUserData => {
        var currentUserObject = currentUserData;
        var foreignUserObject;
        // var follow_object = {
        //     type: "follow",
        //     summary: `${user_first_name} wants to follow ${author_first_name}`,
        // }

        var follow_object = {
            type: "follow",
        }

        // follow_object.actor = currentUserObject;

        let author_url;

        if (author_host.includes("p2psd") || author_host.includes("bigger-yoshi")){
             author_url = new URL("authors/" + author_id, author_host);
        } else {
            author_url = new URL("authors/" + uuidToHex(author_id), author_host);
        }

        getSingleAuthorInfo(author_url, auth_headers).then(foreignUserData => {
            foreignUserObject = foreignUserData;


            const user_name_list = currentUserData.displayName.split(" ");

            const author_name_list = foreignUserData.displayName.split(" ");

            var user_first_name = user_name_list[0];

            var author_first_name = author_name_list[0];


            follow_object.summary = `${user_first_name} wants to follow ${author_first_name}`

            follow_object.actor = currentUserObject;

            follow_object.object = foreignUserObject


            // console.log(follow_object);

            // const foreignAuthorURL = new URL("api/authors/" + author_id + "/inbox", "http://127.0.0.1:8000");
            const foreignAuthorURL = author_url + "/inbox"

            // var headers;

            // if (foreign_node_token){
            //     headers = new Headers({
            //     'Authorization': 'Basic '+foreign_node_token,
            //     'Content-Type': 'application/json'
            //     })
            // } else {
            //     headers = new Headers({
            //     'Content-Type': 'application/json'
            //     })
            // }

            fetch(foreignAuthorURL, {
                method: "POST",
                headers: auth_headers,
                redirect: "follow",
                body: JSON.stringify(follow_object)
            }).then(response => {
                // console.log("-------------Response: ", response.status);
            })

            const addToSentRequestURL = new URL("add-to-sent", `${window.location.protocol}//` + window.location.host);

            const sentRequestObject = {user_id:user_id, author_id:author_id, foreign_user_object: foreignUserObject};

            fetch(addToSentRequestURL, {
                method: "POST",
                redirect: "follow",
                headers: new Headers({
                'Authorization': 'Basic '+btoa('server1:123'),
                'Content-Type': 'application/json'
            }),
                body: JSON.stringify(sentRequestObject)
            });

        })


    });
}

async function getSingleAuthorInfo(url, auth_headers){

    const currentAuthorURL = url;

    const currentAuthorResponse = await fetch(currentAuthorURL, {
        headers: auth_headers, redirect: "follow"});

    const currentAuthorResponseJSON = await currentAuthorResponse.json();

    return currentAuthorResponseJSON;

}

// async function getSingleAuthorInfo(url, token){

//     const currentAuthorURL = url;

//     // console.log(currentAuthorURL);

//     // const currentAuthorURL = new URL("api/authors/" + author_id, "http://127.0.0.1:8000");

//     var headers;

//     if (token){
//         headers = new Headers({
//                 'Authorization': 'Basic '+token,
//                 'Content-Type': 'application/json'
//         })
//     } else {
//         headers = new Headers({
//                 'Content-Type': 'application/json'
//         })
//     }

//     const currentAuthorResponse = await fetch(currentAuthorURL, {
//         headers: headers});

//     const currentAuthorResponseJSON = await currentAuthorResponse.json();

//     return currentAuthorResponseJSON;

// }

function setFollowers(followers, user_id, author_id, author_host, nickname_table) {
    let num = 0;
    if (user_id === author_id) {
        var cardTemplate = document.getElementById('my-followers-card');
    } else {
        var cardTemplate = document.getElementById('followers-card');
    }
    for (let follower of followers) {
        let host = follower.host;
        let hostUrl = new URL(host);
        if (nickname_table[hostUrl.host] != undefined) {
            let nickname = nickname_table[hostUrl.host];
            num++;
            const instance = document.importNode(cardTemplate.content, true);
            let uuid = extractUUID(follower.id);

            if (follower.profileImage !== null && follower.profileImage !== "") $(instance).find(".follower_image").attr("src", follower.profileImage);
            if (follower.github) {
                $(instance).find(".follower_github").attr("href", follower.github);
            } else {
               //$(instance).find(".follower_github").addClass("disabled").css("background-color", "#6E757C");
               $(instance).find(".follower_github").parent().parent().append("<a type='button' class='btn btn-primary follower_profile_link'><i class='bi bi-person-fill'>&nbsp;Profile</i></a>");
               $(instance).find(".follower_github").parent().remove();
            }
            $(instance).find(".follower_profile_link").attr("href", "http://"+server_host+"/authors/"+nickname+"/"+uuid);
            $(instance).find(".follower_display_name").text(follower.displayName);
            $(instance).find(".follower_host").attr("href", host).text(host.replace("http://",''));
            $(instance).find(".removefollower").val(uuid);
            $("#followers_tab_stream").append(instance);
        }
    }
    if (num === 0) {
        $("#followers_tab_stream").text("No followers")
    }
    if (num === 1) {
        $("#nav-followers-tab").text(num + " Follower");
    } else {
        $("#nav-followers-tab").text(num + " Followers");
    }
}

function setFriends(followers, author_id) {
    if (followers.length === 0) {
        $("#nav-friends-tab").text("0 True Friends");
        $("#friends_tab_stream").text("No True Friends");
    } else {
        for (let follower of followers) {
            let hostUrl = new URL (follower.host);
            let hostname = hostUrl.hostname;
            if (token_table[hostname] != undefined) {
                let auth_headers = new Headers({
                    'Authorization': 'Basic '+ token_table[hostname],
                    'Content-Type': 'application/json'
                })

                var url;
                if (follower.host.includes("p2psd")) {
                    if (follower.url.at(-1) == "/")
                        url = new URL(follower.url + "followers/" + author_id + "/");
                    else
                        url = new URL(follower.url + "/followers/" + author_id + "/");
                } else if (follower.host.includes("bigger-yoshi")){
                    //var url = new URL("authors/" + extractUUID(follower.id) + "/followers/" + author_id, author_host);
                    if (follower.url.at(-1) == "/")
                        url = new URL(follower.url + author_host + "authors/" + author_id);
                    else
                        url = new URL(follower.url + "/" + author_host + "authors/" + author_id);
                } else {
                    if (follower.url.at(-1) == "/")
                        url = new URL(follower.url + "followers/" + uuidToHex(author_id));
                    else
                        url = new URL(follower.url + "/followers/" + uuidToHex(author_id));
                }
                fetch(url, {method: "GET", headers: auth_headers,  redirect: "follow",}).then((response) => {
                    if (response.status === 200) { // OK
                        let temp = response.json();
                        //console.log(temp);
                        return temp;
                    } else if (response.status === 404) {
                        return JSON.parse('{"is_following" : "false"}');
                    } else {
                        alert("Something went wrong: " + response.statusText);
                    }
                }).then((data) => {
                    //console.log(isFollowing);
                    let is_following;
                    if (data.is_following != null && String(data.is_following).toLowerCase() === "true") is_following = true;
                    else if (data.accepted != null && String(data.accepted).toLowerCase() === "true") is_following = true;
                    else if (data.approved != null && data.approved === true) is_following = true;
                    else is_following = false;
                    if (is_following) {
                        const cardTemplate = document.getElementById('friends-card');
                        const instance = document.importNode(cardTemplate.content, true);
                        let uuid = extractUUID(follower.id);
                        let host = follower.host;
                        let hostUrl = new URL(host);
                        let nickname = nickname_table[hostUrl.host];
                        if (follower.profileImage !== null && follower.profileImage !== "") {$(instance).find(".friend_image").attr("src", follower.profileImage);}
                        if (follower.github) {
                            $(instance).find(".friend_github").attr("href", follower.github);
                        } else {
                           //$(instance).find(".follower_github").addClass("disabled").css("background-color", "#6E757C");
                           $(instance).find(".friend_github").parent().parent().append("<a type='button' class='btn btn-primary friend_profile_link'><i class='bi bi-person-fill'>&nbsp;Profile</i></a>");
                           $(instance).find(".friend_github").parent().remove();
                        }
                        $(instance).find(".friend_profile_link").attr("href", "http://"+server_host+"/authors/"+nickname+"/"+uuid);
                        $(instance).find(".friend_display_name").text(follower.displayName);
                        $(instance).find(".friend_host").attr("href", host).text(host.replace("http://", ''));
                        $("#friends_tab_stream").append(instance);
                    }
                }).then(() => {
                    let num = document.getElementById("friends_tab_stream").childElementCount;
                    if (num === 1) {
                        $("#nav-friends-tab").text(num + " True Friend");
                    } else {
                        $("#nav-friends-tab").text(num + " True Friends");
                    }
                    if (follower === followers.at(-1)) {
                        if (num == 0) {
                            $("#friends_tab_stream").text("No True Friends");
                        }
                    }
                })
            }
        }
    }
}