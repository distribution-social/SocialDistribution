export function makeAjaxCallAsync(url, method, data, headers, successCallback, errorCallback) {

  return $.ajax({
    url: url,
    method: method,
    data: data,
    headers: headers,
    async: true,
    xhrFields: {
      withCredentials: true
    },
    success: function(response, textStatus, xhr) {
      if (typeof successCallback === 'function') {
        successCallback(response,xhr.status);
      }
    },
    error: function(xhr, textStatus, error) {
      if (typeof errorCallback === 'function') {
        errorCallback(error,xhr.status);
      }
    }
  });
}

export function makeAjaxCall(url, method, data, headers, successCallback, errorCallback) {

  return $.ajax({
    url: url,
    method: method,
    data: data,
    headers: headers,
    async: false,
    xhrFields: {
      withCredentials: true
    },
    success: function(response, textStatus, xhr) {
      if (typeof successCallback === 'function') {
        successCallback(response,xhr.status);
      }
    },
    error: function(xhr, textStatus, error) {
      if (typeof errorCallback === 'function') {
        errorCallback(error,xhr.status);
      }
    }
  });
}