function fetch_menus() {
    fetch('/api/menus')
    .then(response => {
        return response.json()
    })
    .then(data => {
        menus = data;
        update_interface()
    })
    .catch(err => {
        console.log(err)
    })
}

var date_viewed = new Date();
var menus = [];

function update_interface() {
    var ask = date_viewed.print();
//    var ask = "2019-06-14";
    var menu = menus.find(menu => menu["id"] == ask);
    console.log(menu);

    if (menu == null) {
        document.getElementById("N/A").style.display = "block";
        document.getElementById("lunch").style.display = "none";
        document.getElementById("dinner").style.display = "none";
        return;
    }

    document.getElementById("N/A").style.display = "none";
    document.getElementById("lunch").style.display = "block";
    document.getElementById("dinner").style.display = "block";

    // Day
    document.getElementById("day-title-a").innerHTML = menu["day"];
    document.getElementById("day-title-a").innerHTML = menu["day"];

    // Lunch
    document.getElementById("lunch-1a").innerHTML = menu["lunch"]["p1"];
    document.getElementById("lunch-1b").innerHTML = menu["lunch"]["p1"];

    if (menu["lunch"]["p2"] != null) {
        document.getElementById("lunch-2a").innerHTML = menu["lunch"]["p2"];
        document.getElementById("lunch-2b").innerHTML = menu["lunch"]["p2"];
    }

    // Dinner
    document.getElementById("dinner-1a").innerHTML = menu["dinner"]["p1"];
    document.getElementById("dinner-1b").innerHTML = menu["dinner"]["p1"];

    if (menu["dinner"]["p2"] != null) {
        document.getElementById("dinner-2a").innerHTML = menu["dinner"]["p2"];
        document.getElementById("dinner-2b").innerHTML = menu["dinner"]["p2"];
    }

    update_buttons();

}

function update_buttons() {
    var yesterday = new Date();
    var tomorrow = new Date();

    yesterday.setDate(date_viewed.getDate() - 1);
    tomorrow.setDate(date_viewed.getDate() + 1);

    var yesterday_menu = menus.find(menu => menu["id"] == yesterday.print());
    var tomorrow_menu = menus.find(menu => menu["id"] == tomorrow.print());

    if (yesterday_menu == null) {
        document.getElementById("previous").disabled = true;
    } else {
        document.getElementById("previous").disabled = false;
    }

    if (tomorrow_menu == null) {
        document.getElementById("next").disabled = true;
    } else {
        document.getElementById("next").disabled = false;
    }
}

tomorrow = function() {
    date_viewed.setDate(date_viewed.getDate() + 1);
    update_interface();
    update_buttons();
    console.log('tomorrow');
    console.log(date_viewed.print());
}

yesterday = function() {
    date_viewed.setDate(date_viewed.getDate() - 1);
    update_interface();
    update_buttons();
    console.log("yesterday");
    console.log(date_viewed.print());
}

Date.prototype.print = function() {
    var year = this.getFullYear();
    var month = this.getMonth();
    var day = this.getDate();

    if (month < 10) {
        month = "0" + month;
    }

    if (day < 10) {
        day = "0" + day;
    }

    return year + "-" + month + "-" + day;
}

window.onload = fetch_menus;
document.getElementById("next").onclick = tomorrow;
document.getElementById("previous").onclick = yesterday;