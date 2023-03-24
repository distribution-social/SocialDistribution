// References:
//  https://css-tricks.com/crafting-reusable-html-templates/
//  https://dmitripavlutin.com/parse-url-javascript/

import { extractUUID } from "./utility.js";

$(document).ready(function() {
    console.log("host:"+author_host);
    getAndSetProfileCard();

    // get followers from server and use data to set followers and true friends
    const followersUrl = new URL("api/authors/" + author_id + "/followers", "http://127.0.0.1:8000");
    fetch(followersUrl, {method: "GET"}).then((response) => {
        if (response.status === 200) { // OK
            return response.json();
        } else {
            alert("Something went wrong: " + response.status);
        }
    }).then((data) => {
        const followers = data.items;
        setFollowers(followers, user_id, author_id);
        setFriends(followers, author_id);
        return;
    })
});

function getAndSetProfileCard() {
    const authorProfileUrl = new URL("api/authors/" + author_id, "http://127.0.0.1:8000");
    // set profile card info
    fetch(authorProfileUrl, {method: "GET"}).then((response) => {
        if (response.status === 200) { // OK
            return response.json();
        } else {
            alert("Something went wrong: " + response.status);
        }
    }).then((data) => {
        let profileCard = document.getElementById("profile_card");
        $(profileCard).find(".profile_image").attr("src", data.profileImage);
        $(profileCard).find(".profile_github").attr("href", data.github);
        $(profileCard).find(".profile_display_name").text(data.displayName);
        return;
    })
    // handle follow unfollow button
    const authorIsFollowingUrl = new URL("api/authors/" + author_id + "/followers/" + user_id, "http://127.0.0.1:8000");
    fetch(authorIsFollowingUrl, {method: "GET"}).then((response) => {
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
        }
    });


    getSingleAuthorInfo(user_id).then(currentUserData => {
        var currentUserObject = currentUserData;
        var foreignUserObject;
        var follow_object = {
            type: "follow",      
            summary:"Justin wants to follow admin",
        }
        
        follow_object.actor = currentUserObject;

        getSingleAuthorInfo(author_id).then(foreignUserData => {
            foreignUserObject = foreignUserData;
            follow_object.author = foreignUserObject
            console.log(follow_object);
        })


    })

}


async function getSingleAuthorInfo(author_id){

    const currentAuthorURL = new URL("api/authors/" + author_id, "http://127.0.0.1:8000");

    const currentAuthorResponse = await fetch(currentAuthorURL);

    const currentAuthorResponseJSON = await currentAuthorResponse.json();

    return currentAuthorResponseJSON;
  
}

function setFollowers(followers, user_id, author_id) {
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
        $(instance).find(".follower_image").attr("src", follower.profileImage);
        $(instance).find(".follower_profile_link").attr("href", "http://127.0.0.1:8000/authors/"+uuid);
        $(instance).find(".follower_github").attr("href", follower.github);
        $(instance).find(".follower_display_name").text(follower.displayName);
        $(instance).find(".follower_host").attr("href", host).text(host.replace("http://",'').replace("/",''));
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
    let num = 0;
    for (let follower of followers) {
        const url = new URL("api/authors/" + follower.id + "/followers/" + author_id, "http://127.0.0.1:8000");
        fetch(url, {method: "GET"}).then((response) => {
            if (response.status === 200) { // OK
                return true;
            } else if (response.status === 404) {
                // not following, do nothing
                return false;
            } else {
                alert("Something went wrong: " + response.status);
            }
        }).then((isTrueFriend) => {
            if (isTrueFriend) {
                num++;
                const cardTemplate = document.getElementById('friends-card');
                const instance = document.importNode(cardTemplate.content, true);
                let uuid = extractUUID(follower.id);
                let host = follower.host;
                $(instance).find(".friend_image").attr("src", follower.profileImage);
                $(instance).find(".friend_profile_link").attr("href", "http://127.0.0.1:8000/authors/" + uuid);
                $(instance).find(".friend_github").attr("href", follower.github);
                $(instance).find(".friend_display_name").text(follower.displayName);
                $(instance).find(".friend_host").attr("href", host).text(host.replace("http://", '').replace("/", ''));
                $("#friends_tab_stream").append(instance);

                if (num === 0) {
                    $("#friends_tab_stream").text("No followers")
                }
                if (num === 1) {
                    $("#nav-friends-tab").text(num + " True Friend");
                } else {
                    $("#nav-friends-tab").text(num + " True Friends");
                }
            }
            return;
        })
    }
}