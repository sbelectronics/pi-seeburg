COLORS = ["red", "green", "blue", "white", "magenta", "yellow", "cyan",  "black", "orange"];

function seeburg() {
    onQuarter = function() {
        var button_selector = "#quarter";
        console.log("quarter");
        if (seeburg.postUI) {
            seeburg.sendQuarter();
        }
    }

    onDime = function() {
        var button_selector = "#dime";
        console.log("dime");
        if (seeburg.postUI) {
            seeburg.sendDime();
        }
    }

    onNickel = function() {
        var button_selector = "#nickel";
        console.log("nickel");
        if (seeburg.postUI) {
            seeburg.sendNickel();
        }
    }

    sendQuarter = function() {
        $.ajax({url: "/seeburg/insertQuarter"});
    }

    sendDime = function() {
        $.ajax({url: "/seeburg/insertDime"});
    }

    sendNickel = function() {
        $.ajax({url: "/seeburg/insertNickel"});
    }

    initButtons = function() {
        $("#quarter").click(function() { seeburg.onQuarter(); });
        $("#dime").click(function() { seeburg.onDime(); });
        $("#nickel").click(function() { seeburg.onNickel(); });
    }

    start = function() {
         this.postUI = true;
         this.initButtons();
    }

    return this;
}

$(document).ready(function(){
    seeburg = seeburg()
    seeburg.start();
});

