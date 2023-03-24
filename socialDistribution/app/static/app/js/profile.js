// References:
//  https://css-tricks.com/crafting-reusable-html-templates/
//  https://dmitripavlutin.com/parse-url-javascript/

import { extractUUID } from "./utility.js";

$(document).ready(function() {
    console.log("host:"+author_host);
    console.log(auth_headers);

    getAndSetProfileCard();
    setFollowing(serialized_followings, user_id, author_id, author_host);

    // get followers from server and use data to set followers and true friends
    const followersUrl = new URL("authors/" + author_id + "/followers", author_host);
    fetch(followersUrl, {method: "GET", headers: auth_headers}).then((response) => {
        if (response.status === 200) { // OK
            return response.json();
        } else {
            alert("Something went wrong: " + response.status);
        }
    }).then((data) => {
        console.log(data);
        const followers = data.items;
        setFollowers(followers, user_id, author_id, author_host);
        setFriends(followers, author_id);
        return;
    })
});

function getAndSetProfileCard() {
    const authorProfileUrl = new URL("authors/" + author_id, author_host);
    // set profile card info
    fetch(authorProfileUrl, {method: "GET", headers: auth_headers}).then((response) => {
        if (response.status === 200) { // OK
            return response.json();
        } else {
            alert("Something went wrong: " + response.status);
        }
    }).then((data) => {
        let profileCard = document.getElementById("profile_card");
        console.log("img: "+ data.profileImage);
        if (data.profileImage !== null) {$(profileCard).find(".profile_image").attr("src", data.profileImage);}
        $(profileCard).find(".profile_github").attr("href", data.github);
        $(profileCard).find(".profile_display_name").text(data.displayName);
        return;
    })
    // handle follow unfollow button
    const authorIsFollowingUrl = new URL("authors/" + author_id + "/followers/" + user_id, author_host);
    fetch(authorIsFollowingUrl, {method: "GET", headers: auth_headers}).then((response) => {
        if (response.status === 200) { // OK
            // following
            $("#follow_unfollow_button").attr("name", "unfollow").val(author_id).text("Unfollow");
            return;
        } else if (response.status === 404) {
            // not following
            $("#follow_unfollow_button").attr("name", "follow").val(author_id).text("Request to Follow");
            return;
        } else {
            alert("Something went wrong: " + response.status);
        }
    })
}

function setFollowers(followers, user_id, author_id, author_host) {
    let num = 0;
    console.log("user: "+user_id+"    author: "+ author_id);
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
        if (follower.profileImage !== null) {$(instance).find(".follower_image").attr("src", follower.profileImage);}
        $(instance).find(".follower_profile_link").attr("href", author_host+"/authors/"+uuid);
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
        const url = new URL("authors/" + extractUUID(follower.id) + "/followers/" + author_id, author_host);
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
                if (follower.profileImage !== null) {$(instance).find(".friend_image").attr("src", follower.profileImage);}
                $(instance).find(".friend_profile_link").attr("href", author_host + "/authors/" + uuid);
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
        if (follow.profileImage !== null) {$(instance).find(".following_image").attr("src", follow.profileImage);}
        $(instance).find(".following_profile_link").attr("href", follow.host+"/authors/"+uuid); // TODO: switch to server host
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