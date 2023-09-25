$(function(){

    ajax('http://localhost:3333/api/getusers', {}, displayAdministrationData);
    refreshWallet();
    $("#name-modal .cancel-button").click(function(event) {
        $("#name-modal.modal-background").hide();
        $("#name-modal .confirm-button").unbind("click");
    });
    $("#country-modal .cancel-button").click(function(event) {
        $("#country-modal.modal-background").hide();
        $("#country-modal .confirm-button").unbind("click");
    });
    $("#role-modal .cancel-button").click(function(event) {
        $("#role-modal.modal-background").hide();
        $("#role-modal .confirm-button").unbind("click");
    });

    function displayAdministrationData(data) {
        let container = $("#user-administration").empty();
        let table = $("<table>").addClass("styled-table");
        let thead = $("<thead>").append($("<tr>").append($("<th>").text("ID"))
            .append($("<th>").text("Email"))
            .append($("<th>").text("Name"))
            .append($("<th>"))
            .append($("<th>").text("Country"))
            .append($("<th>"))
            .append($("<th>").text("Wallet"))
            .append($("<th>").text("Role"))
            .append($("<th>"))
        );
        table.append(thead);
        let tbody = $("<tbody>");
        for (var i = 0; i < data.length; i++) {
            let row = $("<tr>");
            let edit_name = $("<img>").attr("src", "./static/edit.png").attr("width", "18").attr("user-id", data[i].id).addClass("edit-name");
            edit_name.click(editName);
            let edit_country = $("<img>").attr("src", "./static/edit.png").attr("width", "18").attr("user-id", data[i].id).addClass("edit-country");
            edit_country.click(editCountry);
            let edit_role = $("<img>").attr("src", "./static/edit.png").attr("width", "18").attr("user-id", data[i].id).addClass("edit-role");
            edit_role.click(editRole);
            row.append($("<td>").text(data[i].id)).append($("<td>").text(data[i].email))
                .append($("<td>").text(data[i].name)).append($("<td>").html(edit_name))
                .append($("<td>").text(data[i].country)).append($("<td>").html(edit_country))
                .append($("<td>").text(data[i].wallet)).append($("<td>").text(data[i].role))
                .append($("<td>").html(edit_role));
            tbody.append(row);
        }
        table.append(tbody);
        container.append(table);

    }

    function editName(event) {
        let button = $(event.target);
        let user_id = parseInt(button.attr("user-id"));
        let prev = button.parent().prev();
        let modal = $("#name-modal");
        modal.find("p").text("Please enter the new name for id: " + user_id);
        $("#name-modal .modal-input").val(prev.text());
        modal.show();
        $("#name-modal .confirm-button").bind("click", {user_id: user_id}, pushEditName);
    }

    function pushEditName(event) {
        let new_name = $("#name-modal .modal-input").val();
        ajax("http://localhost:3333/api/changeusername", { user_id: event.data.user_id, new_name: new_name }, confirmEditName);
        $("#name-modal").hide();
        $("#name-modal .confirm-button").unbind("click");
        // lock edit button
    }

    function confirmEditName(data) {
        if (data.message == "success") {
            let button = $(".edit-name[user-id='" + data.user_id + "']");
            button.parent().prev().text(data.new_name);
        } else {
            displayMessage("failed - " + data.reason);
        }
    }

    function editCountry(event) {
        let button = $(event.target);
        let user_id = parseInt(button.attr("user-id"));
        let modal = $("#country-modal");
        modal.find("p").text("Please enter the new country");
        $("#country-modal .modal-input").val();
        modal.show();
        $("#country-modal .confirm-button").bind("click", {user_id: user_id}, pushEditCountry);
    }

    function pushEditCountry(event) {
        let new_country_id = $("#country-modal .modal-input").val();
        ajax("http://localhost:3333/api/changeusercountry", { user_id: event.data.user_id, new_country_id: new_country_id }, confirmEditCountry);
        $("#country-modal").hide();
        $("#country-modal .confirm-button").unbind("click");
        // lock edit button
    }

    function confirmEditCountry(data) {
        if (data.message == "success") {
            let button = $(".edit-country[user-id='" + data.user_id + "']");
            button.parent().prev().text(data.new_country_name);
        } else {
            displayMessage("failed - " + data.reason);
        }
    }

    function editRole(event) {
        let button = $(event.target);
        let user_id = parseInt(button.attr("user-id"));
        let modal = $("#role-modal");
        modal.find("p").text("Please select the new role");
        $("#role-modal .modal-input").val();
        modal.show();
        $("#role-modal .confirm-button").bind("click", {user_id: user_id}, pushEditRole);
    }

    function pushEditRole(event) {
        let new_role = $("#role-modal .modal-input").val();
        ajax("http://localhost:3333/api/changeuserrole", { user_id: event.data.user_id, new_role: new_role }, confirmEditRole);
        $("#role-modal").hide();
        $("#role-modal .confirm-button").unbind("click");
        // lock edit button
    }

    function confirmEditRole(data) {
        if (data.message == "success") {
            let button = $(".edit-role[user-id='" + data.user_id + "']");
            button.parent().prev().text(data.new_role);
        } else {
            displayMessage("failed - " + data.reason);
        }
    }

});
