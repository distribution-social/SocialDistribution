export async function fetchActivitiesJSON(username) {
  const response = await fetch(`${window.location.protocol}//${window.location.host}/github/${username}`);
  const activities = await response.json();
  return activities;
}

//gets the gtihub username
export function getGitHubUsername(github_url){
    let github_username;
    try {
        const url_array = github_url.split("/");
        github_username = url_array[3];
    }
    catch(err) {
        github_username = null;
    }
    finally {
        return github_username;
    }
}

function formatEvent(event){

    const event_array = event.split(":");

    event = event_array[2].split("/")[0];

    return event;
}

function formatDateTime(datetime){
    const format_datetime = new Date(datetime);
    const month = format_datetime.toLocaleString('default', { month: 'long' });
    const day = format_datetime.getDate();
    const year = format_datetime.getFullYear();
    const time = format_datetime.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });
    return `${month} ${day}, ${year} (${time})`;
}

function formatTitle(title){
    // https://stackoverflow.com/questions/6871403/how-can-i-delete-the-first-word-from-a-line
    const result = title.substr(title.indexOf(" ") + 1);

    const capitalized = result.charAt(0).toUpperCase() + result.slice(1)

    return capitalized;
}

//create the html for each github event
export function createHTMLCard(event, link, title, published, updated, authors) {

    let html_element = `
<div class="card mb-3" style="max-width: 600px;">
   <div class="card-header">
      <b>${formatEvent(event)} by <a href="${authors[0].href}" style="text-decoration:none">${authors[0].name}</a></b>
   </div>
   <div class="row g-0">
      <!-- <div class="col-md-4">
         <img src="https://avatars.githubusercontent.com/u/26825560?s=200&v=4" class="img-fluid rounded-start" alt="...">
         </div> -->
      <div class="col-md-8">
         <div class="card-body">
            <h5 class="card-title"><a href=${link} style="text-decoration:none">${formatTitle(title)}</a></h5>
            <p class="card-text"><small class="text-body-secondary"> ${formatDateTime(published)} </small></p>
         </div>
      </div>
   </div>
</div>
`;
    return html_element
}

