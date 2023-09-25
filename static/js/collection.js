$(function(){

    ajax('http://localhost:3333/api/collection', {}, displayCollection);
    refreshWallet();
    $(".cancel-button").click(function(event) {
        $(".modal-background").hide();
        $(".confirm-button").unbind("click");
    });

    function displayCollection(data) {
        let container = $(".players-selection").empty();
        for (var i = 0; i < data.length; i++) {
            let tile = $("<div>").addClass("player-tile").attr("card-id", data[i].id);
            let row = $("<div>").addClass("row");
            row.append($("<img>").addClass("player-img").attr("src", "./static/players/" + data[i].id + ".png"));
            let stats = $("<div>").addClass("player-stats");
            let ratings = $("<div>").addClass("player-ratings");
            ratings.append($("<div>").addClass("rating r1").text(data[i].current_skill));
            ratings.append($("<div>").addClass("rating r1").text(data[i].potential_skill));
            stats.append(ratings);
            stats.append($("<div>").addClass("player-age").text("Age: " + data[i].age))
            row.append(stats);
            tile.append(row)
            tile.append($("<div>").addClass("player-name").text(data[i].name));
            tile.append($("<div>").addClass("player-price").text("Market Value: " + data[i].market_value));
            let button = $("<div>").addClass("action-button").attr("card-id", data[i].id);
            if (data[i].on_market == "yes") {
                tile.append($("<div>").addClass("player-price").text("Asking Price: " + data[i].asking_price));
                button.text("Remove");
                button.click(removeFromMarket);
            } else {
                tile.append($("<div>").addClass("player-price").html("&nbsp;"));
                button.text("Sell");
                button.click(addToMarket);
            }
            tile.append(button);
            container.append(tile);
        }

    }

    function addToMarket(event) {
        let modal = $(".modal-background");
        let tile = $(event.target).closest(".player-tile");
        let name = tile.find(".player-name").text();
        modal.find("p").text("Set the price for " + name);
        modal.show();
        let player_id = parseInt($(event.target).attr("card-id"));
        $(".confirm-button").bind("click", { player_id: player_id}, pushToMarket);
    }

    function pushToMarket(event) {
        let asking_price = parseInt($(".modal-input").val());
        ajax("http://localhost:3333/api/addtomarket",
            { card_id: event.data.player_id, asking_price: asking_price },
            confirmPushToMarket
        );
        $(".modal-background").hide();
        $(".confirm-button").unbind("click");
        let tile = $(".player-tile[card-id='" + event.data.player_id + "']");
        let button = tile.find(".action-button");
        button.unbind("click");
        button.addClass("locked");
    }

    function confirmPushToMarket(data) {
        if (data.message == "success") {
            let tile = $(".player-tile[card-id='" + data.card_id + "']");
            let button = tile.find(".action-button");
            button.removeClass("locked");
            button.text("remove");
            button.click(removeFromMarket);
            tile.find(".player-price").last().text("Asking Price: " + data.asking_price);
        }
    }

    function removeFromMarket(event) {
        let button = $(event.target);
        let card_id = parseInt(button.attr("card-id"));
        button.unbind("click");
        button.addClass("locked");
        ajax("http://localhost:3333/api/removefrommarket",
            { card_id: card_id },
            confirmRemoveFromMarket
        );
    }

    function confirmRemoveFromMarket(data) {
        if (data.message == "success") {
            let tile = $(".player-tile[card-id='" + data.card_id + "']");
            let button = tile.find(".action-button");
            button.text("sell");
            button.unbind("click");
            button.click(addToMarket);
            button.removeClass("locked");
            tile.find(".player-price").last().html("&nbsp;");
        } else {
            displayMessage("can't remove - card has be bought");
        }
    }

});