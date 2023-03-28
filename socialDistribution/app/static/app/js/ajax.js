export function makeAjaxCall(url, method, data, successCallback, errorCallback) {
  $.ajax({
    url: url,
    method: method,
    data: data,
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