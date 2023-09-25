$(function(){

    ajax('http://localhost:3333/api/my-account', {}, displayAccountData);
    refreshWallet();
    $("#name-modal .cancel-button").click(function(event) {
        $("#name-modal.modal-background").hide();
        $("#name-modal .confirm-button").unbind("click");
    });
    $("#country-modal .cancel-button").click(function(event) {
        $("#country-modal.modal-background").hide();
        $("#country-modal .confirm-button").unbind("click");
    });

    function displayAccountData(data) {
        let container = $("#account-details");
        container.empty();
        let img1 = $("<img>").attr("src", "./static/edit.png").attr("width", "22").attr("id", "edit-name");
        let img2 = $("<img>").attr("src", "./static/edit.png").attr("width", "22").attr("id", "edit-country");
        let row1 = $("<div>").addClass("account-row");
        row1.append($("<div>").addClass("account-row-label").text("Name:"))
            .append($("<div>").addClass("account-row-value").text(data.name).attr("id", "name-value"))
            .append($("<div>").addClass("account-row-edit").append(img1));
        let row2 = $("<div>").addClass("account-row");
        row2.append($("<div>").addClass("account-row-label").text("Role:"))
            .append($("<div>").addClass("account-row-value").text(data.role));
        let row3 = $("<div>").addClass("account-row");
        row3.append($("<div>").addClass("account-row-label").text("Country:"))
            .append($("<div>").addClass("account-row-value").text(data.country).attr("id", "country-value"))
            .append($("<div>").addClass("account-row-edit").append(img2));
        let row4 = $("<div>").addClass("account-row");
        row4.append($("<div>").addClass("account-row-label").text("Collection:"))
            .append($("<div>").addClass("account-row-value").text(data.collection));
        container.append(row1).append(row2).append(row3).append(row4);
        $("#edit-name").click(editName);
        $("#edit-country").click(editCountry);
    }

    function editName(event) {
        let modal = $("#name-modal");
        modal.find("p").text("Please enter the new name");
        $("#name-modal .modal-input").val($("#name-value").text());
        modal.show();
        $("#name-modal .confirm-button").bind("click", {}, pushEditName);
    }

    function pushEditName() {
        let new_name = $("#name-modal .modal-input").val();
        ajax("http://localhost:3333/api/changename", { new_name: new_name }, confirmEditName);
        $("#name-modal").hide();
        $("#name-modal .confirm-button").unbind("click");
        // lock edit button
    }

    function confirmEditName(data) {
        if (data.message == "success") {
            $("#name-value").text(data.new_name);
        }
    }

    function editCountry(event) {
        let modal = $("#country-modal");
        modal.find("p").text("Please enter the new country");
        $("#country-modal .modal-input").val($("#country-value").text());
        modal.show();
        $("#country-modal .confirm-button").bind("click", {}, pushEditCountry);
    }

    function pushEditCountry() {
        let new_country_id = $("#country-modal .modal-input").val();
        ajax("http://localhost:3333/api/changecountry", { new_country_id: new_country_id }, confirmEditCountry);
        $("#country-modal").hide();
        $("#country-modal .confirm-button").unbind("click");
        // lock edit button
    }

    function confirmEditCountry(data) {
        if (data.message == "success") {
            $("#country-value").text(data.new_country_name);
        }
    }

});