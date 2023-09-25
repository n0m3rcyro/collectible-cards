$(function(){

    ajax('http://localhost:3333/api/marketplace', {}, displayMarketplace);
    refreshWallet();

    function displayMarketplace(data) {

        let ownItems = $("#own-items").empty();
        let othersItems = $("#others-items").empty();

        for (var i = 0; i < data.length; i++) {
            let tile = $("<div>").addClass("player-tile").attr("card-id", data[i].card_id);
            let row = $("<div>").addClass("row");
            row.append($("<img>").addClass("player-img").attr("src", "./static/players/" + data[i].card_id + ".png"));
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
            let button = $("<div>").addClass("action-button").attr("card-id", data[i].card_id);
            tile.append($("<div>").addClass("player-price").text("Asking Price: " + data[i].asking_price));
            if (data[i].validity == "invalid") {
                button.text("Remove");
                button.click(removeFromMarket);
            } else {
                button.text("Buy");
                button.click(buyCard);
            }
            tile.append(button);
            if (data[i].validity == "invalid") {
                ownItems.append(tile);
            } else {
                othersItems.append(tile);
            }

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
            let tile = $(".player-tile[card-id='" + data.card_id + "']").remove();
        } else {
            displayMessage("can't remove - card has be bought");
        }
    }

    function buyCard(event) {
        let button = $(event.target);
        let card_id = parseInt(button.attr("card-id"));
        ajax("http://localhost:3333/api/buyfrommarket",
            { card_id: card_id },
            confirmBuyFromMarket
        );
        button.unbind("click");
        button.addClass("locked");
    }

    function confirmBuyFromMarket(data) {
        if (data.message == "success") {
            let card = $(".player-tile[card-id='" + data.card_id + "']");
            card.remove();
            refreshWallet();
        } else if (data.message == "unsuccessful") {
            let button = $(".action-button[card-id='" + data.card_id + "']");
            button.removeClass("locked");
            button.click(buyCard);
            displayMessage(data.reason);
        }
    }

});