// References:
//  https://css-tricks.com/crafting-reusable-html-templates/
//  https://dmitripavlutin.com/parse-url-javascript/

import { extractUUID } from "./utility.js";

$(document).ready(function() {
    console.log("host:"+author_host);
    /*
    const authorUrl = new URL("api/authors/" + author_id, "http://127.0.0.1:8000");
    fetch(authorUrl, {method: "GET"}).then((response) => {
        if (response.status === 200) { // OK
            return response.json();
        } else {
            alert("Something went wrong: " + response.status);
        }
    }).then((data) => {
        setProfile(data);
        return;
    })
    */
    const followersUrl = new URL("api/authors/" + author_id + "/followers", author_host);
    fetch(followersUrl, {method: "GET"}).then((response) => {
        if (response.status === 200) { // OK
            return response.json();
        } else {
            alert("Something went wrong: " + response.status);
        }
    }).then((data) => {
        const followers = data.items;
        setFollowers(followers, user_id, author_id);
        //setFriends(followers, author_id);
        return;
    })
});

function setProfile(profile) {

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
        const followersUrl = new URL("api/authors/" + follower.id + "/followers/" + author_id, "http://127.0.0.1:8000");
        fetch(authorUrl, {method: "GET"}).then((response) => {
            if (response.status === 200) { // OK
                return true;
            } else if (response.status === 404) {
                // not following, do nothing
            } else {
                alert("Something went wrong: " + response.status);
            }
        }).then((isTrueFriend) => {
            num++;
            const cardTemplate = document.getElementById('followers-card');
            const instance = document.importNode(cardTemplate.content, true);
            let uuid = extractUUID(follower.id);
            let host = follower.host;
            $(instance).find(".follower_image").attr("src", follower.profileImage);
            $(instance).find(".follower_profile_link").attr("href", "http://127.0.0.1:8000/authors/" + uuid);
            $(instance).find(".follower_github").attr("href", follower.github);
            $(instance).find(".follower_display_name").text(follower.displayName);
            $(instance).find(".follower_host").attr("href", host).text(host.replace("http://", '').replace("/", ''));
            $(instance).find(".removefollower").val(uuid);
            $("#followers_tab_stream").append(instance);
        
            if (num === 0) {
                $("#friends_tab_stream").text("No followers")
            }
            if (num === 1) {
                $("#nav-friends-tab").text(num + " True Friend");
            } else {
                $("#nav-friends-tab").text(num + " True Friends");
            }
            return;
        })
    }
}