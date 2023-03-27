// References:
//  https://css-tricks.com/crafting-reusable-html-templates/
//  https://dmitripavlutin.com/parse-url-javascript/

import { extractUUID, uuidToHex } from "./utility.js";


$(document).ready(function() {
    console.log("host:"+author_host);

    getAndSetProfileCard();
    setFollowing(serialized_followings, user_id, author_id, author_host);

    // get followers from server and use data to set followers and true friends
    const followersUrl = new URL("authors/" + uuidToHex(author_id) + "/followers", author_host);
    fetch(followersUrl, {method: "GET", headers: auth_headers}).then((response) => {
        if (response.status === 200) { // OK
            return response.json();
        } else {
            alert("Something went wrong: " + response.status);
        }
    }).then((data) => {
        const followers = data.items;
        setFollowers(followers, user_id, author_id, author_host);
        setFriends(followers, author_id);
        return;
    })
});

function getAndSetProfileCard() {
    const authorProfileUrl = new URL("authors/" + uuidToHex(author_id), author_host);
    // set profile card info
    fetch(authorProfileUrl, {method: "GET"}).then((response) => {
        if (response.status === 200) { // OK
            return response.json();
        } else {
            alert("Something went wrong: " + response.status);
        }
    }).then((data) => {
        let profileCard = document.getElementById("profile_card");
        if (data.profileImage !== null && data.profileImage !== "") {$(profileCard).find(".profile_image").attr("src", data.profileImage);}
        $(profileCard).find(".profile_github").attr("href", data.github);
        $(profileCard).find(".profile_display_name").text(data.displayName);
        return;
    })
    // handle follow unfollow button
    const authorIsFollowingUrl = new URL("authors/" + uuidToHex(author_id) + "/followers/" + uuidToHex(user_id), author_host);
    fetch(authorIsFollowingUrl, {method: "GET", headers: auth_headers}).then((response) => {
        // console.log(response.json().is_following);
        if (response.status === 200) { // OK
            // following
            // $("#follow_unfollow_button").attr("name", "unfollow").val(author_id).text("Unfollow");
            return response.json();
        } else if (response.status === 404) {
            // not following
            // $("#follow_unfollow_button").attr("name", "follow").val(author_id).text("Request to Follow");
            return response.json();
        } else {
            alert("Something went wrong: " + response.statusText);
        }
    }).then((result) => {
        // console.log(result.is_following);
        console.log(author_id, user_id);
        if (result.is_following === true){
            $("#follow_unfollow_button").attr("name", "unfollow").val(author_id).text("Unfollow");
        } else {
            $("#follow_unfollow_button").attr("name", "follow").val(author_id).text("Request to Follow");
            const element = document.getElementById("follow_unfollow_button");
            if (element) {
                element.addEventListener("click", sendFollowRequestToInbox);
            }
  
        }
    });

}

function sendFollowRequestToInbox(e){

        e.preventDefault();

        const element = document.getElementById("follow_unfollow_button");

        element.innerText = "Pending Follow Request";

        element.setAttribute('disabled', '');

        const user_name_list = user_display_name.split(" ");

        const author_name_list = author_display_name.split(" ");

        var user_first_name = user_name_list[0];

        var author_first_name = author_name_list[0];

        console.log(user_first_name, author_first_name);

        getSingleAuthorInfo(user_url, local_node_token).then(currentUserData => {
        var currentUserObject = currentUserData;
        var foreignUserObject;
        var follow_object = {
            type: "follow",      
            summary: `${user_first_name} wants to follow ${author_first_name}`,
        }

        follow_object.actor = currentUserObject;

        getSingleAuthorInfo(author_url, foreign_node_token).then(foreignUserData => {
            foreignUserObject = foreignUserData;
            follow_object.object = foreignUserObject
            // console.log(follow_object);

            // const foreignAuthorURL = new URL("api/authors/" + author_id + "/inbox", "http://127.0.0.1:8000");
            const foreignAuthorURL = author_url + "/inbox"

            var headers;

            if (foreign_node_token){
                headers = new Headers({
                'Authorization': 'Basic '+foreign_node_token, 
                'Content-Type': 'application/json'
                })
            } else {
                headers = new Headers({
                'Content-Type': 'application/json'
                })
            }
            
            fetch(foreignAuthorURL, {
                method: "POST",
                headers: headers, 
                body: JSON.stringify(follow_object)
            }).then(response => {
                console.log("-------------Response: ", response.status);
            })
            
            const addToSentRequestURL = new URL("add-to-sent", `${window.location.protocol}//` + window.location.host);
            
            const sentRequestObject = {user_id:user_id, author_id:author_id};

            fetch(addToSentRequestURL, {
                method: "POST",
                headers: new Headers({
                'Authorization': 'Basic '+btoa('server1:123'), 
                'Content-Type': 'application/json'
            }),
                body: JSON.stringify(sentRequestObject)
            });

        })


    });
}

async function getSingleAuthorInfo(url, token){

    const currentAuthorURL = url;

    // console.log(currentAuthorURL);

    // const currentAuthorURL = new URL("api/authors/" + author_id, "http://127.0.0.1:8000");

    var headers;

    if (token){
        headers = new Headers({
                'Authorization': 'Basic '+token, 
                'Content-Type': 'application/json'
        })
    } else {
        headers = new Headers({
                'Content-Type': 'application/json'
        })
    }

    const currentAuthorResponse = await fetch(currentAuthorURL, {
        headers: headers});

    const currentAuthorResponseJSON = await currentAuthorResponse.json();

    return currentAuthorResponseJSON;
  
}

function setFollowers(followers, user_id, author_id, author_host) {
    let num = 0;
    if (user_id === author_id) {
        var cardTemplate = document.getElementById('my-followers-card');
    } else {
        var cardTemplate = document.getElementById('followers-card');
    }
    for (let follower of followers) {
        num++;
        const instance = document.importNode(cardTemplate.content, true);
        let uuid = extractUUID(follower.id);
        let host = follower.host;
        if (follower.profileImage !== null && follower.profileImage !== "") {$(instance).find(".follower_image").attr("src", follower.profileImage);}
        $(instance).find(".follower_profile_link").attr("href", "http://"+server_host+"/authors/"+uuid);
        $(instance).find(".follower_github").attr("href", follower.github);
        $(instance).find(".follower_display_name").text(follower.displayName);
        $(instance).find(".follower_host").attr("href", host).text(host.replace("http://",''));
        $(instance).find(".removefollower").val(uuid);
        $("#followers_tab_stream").append(instance);
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
    let num2 = 0;
    for (let follower of followers) {
        const url = new URL("authors/" + uuidToHex(extractUUID(follower.id)) + "/followers/" + uuidToHex(author_id), author_host);
        fetch(url, {method: "GET", headers: auth_headers}).then((response) => {
            if (response.status === 200) { // OK
                return response.json();
            } else {
                alert("Something went wrong: " + response.status);
            }
        }).then((data) => {
            console.log(data);
            if (data.is_following) {
                num2++;
                const cardTemplate = document.getElementById('friends-card');
                const instance = document.importNode(cardTemplate.content, true);
                let uuid = extractUUID(follower.id);
                let host = follower.host;
                if (follower.profileImage !== null && follower.profileImage !== "") {$(instance).find(".friend_image").attr("src", follower.profileImage);}
                $(instance).find(".friend_profile_link").attr("href", "http://"+server_host+"/authors/" + uuid);
                $(instance).find(".friend_github").attr("href", follower.github);
                $(instance).find(".friend_display_name").text(follower.displayName);
                $(instance).find(".friend_host").attr("href", host).text(host.replace("http://", ''));
                $("#friends_tab_stream").append(instance);

                if (num2 === 0) {
                    $("#friends_tab_stream").text("No followers")
                }
                if (num2 === 1) {
                    $("#nav-friends-tab").text(num2 + " True Friend");
                } else {
                    $("#nav-friends-tab").text(num2 + " True Friends");
                }
            }
            return;
        })
    }
}

function setFollowing(following, user_id, author_id, author_host) {
    let num = 0;
    if (user_id === author_id) {
        var cardTemplate = document.getElementById('my-following-card');
    } else {
        var cardTemplate = document.getElementById('following-card');
    }
    for (let follow of following) {
        num++;
        const instance = document.importNode(cardTemplate.content, true);
        let host = follow.host;
        let uuid = extractUUID(follow.id);
        if (follow.profileImage !== null && follow.profileImage !== "") {$(instance).find(".following_image").attr("src", follow.profileImage);}
        $(instance).find(".following_profile_link").attr("href", "http://"+server_host+"/authors/"+uuid); // TODO: switch to server host
        $(instance).find(".following_github").attr("href", follow.github);
        $(instance).find(".following_display_name").text(follow.displayName);
        $(instance).find(".following_host").attr("href", host).text(host.replace("http://",''));
        $(instance).find(".unfollow").val(uuid);
        $("#followings_tab_stream").append(instance);
    }
    if (num === 0) {
        $("#followings_tab_stream").text("Not following anyone")
    }
    if (num === 1) {
        $("#nav-following-tab").text(num + " Following");
    } else {
        $("#nav-following-tab").text(num + " Followings");
    }
}