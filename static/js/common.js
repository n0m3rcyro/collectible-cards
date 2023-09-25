function ajax(url, postData, callbackFunction, callbackParams = {}) {
    $.ajax({method: "POST", url: url, data: postData}).done(function (data) {
        callbackFunction(data, callbackParams);
    }).fail(function (jqxhr, textStatus, error) {
        console.log('error: ' + textStatus);
    });
}

function refreshWallet() {
    ajax('http://localhost:3333/api/getwallet', {}, uiRefreshWallet);
}

function uiRefreshWallet(data) {
    $("#wallet").text(data.wallet);
}

function displayMessage(message) {
    let id = Math.floor(Math.random() * 10000);
    let ms = $("<div>").addClass("message").attr("id", "message-" + id).text(message);
    $("body").append(ms);
    setTimeout(removeMessage, 3000, id);
}

function removeMessage(id) {
    $("#message-" + id).remove();
}