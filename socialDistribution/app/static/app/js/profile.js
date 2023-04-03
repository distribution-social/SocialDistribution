// References:
//  https://css-tricks.com/crafting-reusable-html-templates/
//  https://dmitripavlutin.com/parse-url-javascript/
//  https://stackoverflow.com/questions/3216013/get-the-last-item-in-an-array
//  https://www.w3schools.com/jsref/prop_element_childelementcount.asp

import { extractUUID, uuidToHex } from "./utility.js";


$(document).ready(function() {
    console.log("host:"+author_host);
    console.log(auth_headers)

    getAndSetProfileCard();
    //setFollowing(serialized_followings, user_id, author_id, author_host);

    // get followers from server and use data to set followers and true friends
    var followersUrl;
    if (author_host.includes("p2psd") || author_host.includes("bigger-yoshi")){
        followersUrl = new URL("authors/" + author_id + "/followers", author_host);
    } else {
        followersUrl = new URL("authors/" + uuidToHex(author_id) + "/followers", author_host);
    }
    console.log(auth_headers);
    fetch(followersUrl, {method: "GET", headers: auth_headers}).then((response) => {
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
    let authorProfileUrl;
    if (author_host.includes("p2psd") || author_host.includes("bigger-yoshi")){
        authorProfileUrl = new URL("authors/" + author_id, author_host);
    } else {
        authorProfileUrl = new URL("authors/" + uuidToHex(author_id), author_host);
    }

    console.log(author_host);
    // set profile card info
    fetch(authorProfileUrl, {method: "GET", headers: auth_headers}).then((response) => {
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
    let authorIsFollowingUrl;
    if (author_host.includes("p2psd") || author_host.includes("bigger-yoshi")){
        authorIsFollowingUrl = new URL("authors/" + author_id + "/followers/" + user_id, author_host);
    } else {
        authorIsFollowingUrl = new URL("authors/" + uuidToHex(author_id) + "/followers/" + uuidToHex(user_id), author_host);
    }

    fetch(authorIsFollowingUrl, {method: "GET", headers: auth_headers}).then((response) => {
        // console.log(response.json().is_following);
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
        console.log(data)
        let is_following;
        if (data.is_following != null && String(data.is_following).toLowerCase() === "true") is_following = true;
        else if (data.accepted != null && String(data.accepted).toLowerCase() === "true") is_following = true;
        else is_following = false;
        if (is_following) {
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

            console.log(user_first_name, author_first_name);

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

async function getSingleAuthorInfo(url, auth_headers){

    const currentAuthorURL = url;

    const currentAuthorResponse = await fetch(currentAuthorURL, {
        headers: auth_headers});

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
        num++;
        const instance = document.importNode(cardTemplate.content, true);
        let uuid = extractUUID(follower.id);
        let host = follower.host;
        let hostUrl = new URL(host);
        let nickname = nickname_table[hostUrl.host];
        if (follower.profileImage !== null && follower.profileImage !== "") {$(instance).find(".follower_image").attr("src", follower.profileImage);}
        $(instance).find(".follower_profile_link").attr("href", "http://"+server_host+"/authors/"+nickname+"/"+uuid);
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
    if (followers.length === 0) {
        $("#nav-friends-tab").text("0 True Friends");
        $("#friends_tab_stream").text("No True Friends");
    } else {
        for (let follower of followers) {
            if (author_host.includes("p2psd") || author_host.includes("bigger-yoshi")){
                var url = new URL("authors/" + uuidToHex(extractUUID(follower.id)) + "/followers/" + author_id, author_host);
            } else {
                var url = new URL("authors/" + uuidToHex(extractUUID(follower.id)) + "/followers/" + uuidToHex(author_id), author_host);
            }
            //const url = new URL("authors/" + uuidToHex(extractUUID(follower.id)) + "/followers/" + uuidToHex(author_id), author_host);
            fetch(url, {method: "GET", headers: auth_headers}).then((response) => {
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
                console.log(data)
                let is_following;
                if (data.is_following != null && String(data.is_following).toLowerCase() === "true") is_following = true;
                else if (data.accepted != null && String(data.accepted).toLowerCase() === "true") is_following = true;
                else is_following = false;
                if (is_following) {
                    const cardTemplate = document.getElementById('friends-card');
                    const instance = document.importNode(cardTemplate.content, true);
                    let uuid = extractUUID(follower.id);
                    let host = follower.host;
                    let hostUrl = new URL(host);
                    let nickname = nickname_table[hostUrl.host];
                    console.log("Nickname: "+nickname);
                    if (follower.profileImage !== null && follower.profileImage !== "") {$(instance).find(".friend_image").attr("src", follower.profileImage);}
                    $(instance).find(".friend_profile_link").attr("href", "http://"+server_host+"/authors/"+nickname+"/"+uuid);
                    $(instance).find(".friend_github").attr("href", follower.github);
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