var date_viewed = new Date();
const days = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];

// Add loader
document.getElementById("N/A").style.display = "none";
document.getElementById("lunch").style.display = "none";
document.getElementById("dinner").style.display = "none";

function fetch_menus() {
    var force = get('force') || get('f')
    console.log('force: ' + force);

    var url = '/api/menus'
    if (force) url += '?force';

    fetch(url)
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

function get_day_title() {
    var day = days[date_viewed.getDay()];
    return day + " " + date_viewed.getDate();
}

function update_interface() {
    var ask = date_viewed.print();
    var menu = menus.find(menu => menu["id"] == ask);

    console.log('Día: ' + ask);
    console.log(menu);

    document.getElementById("loader").style.display = "none";

    if (menu == null) {
        document.getElementById("N/A").style.display = "block";
        document.getElementById("lunch").style.display = "none";
        document.getElementById("dinner").style.display = "none";

        document.getElementById("day-title-a").innerHTML = get_day_title();
        document.getElementById("day-title-a").href = PRINCIPAL_URL;
        document.getElementById("day-title-b").innerHTML = get_day_title();
        document.getElementById("day-title-b").href = PRINCIPAL_URL;
        return;
    }

    document.getElementById("N/A").style.display = "none";
    document.getElementById("lunch").style.display = "block";
    document.getElementById("dinner").style.display = "block";

    // Day
    document.getElementById("day-title-a").innerHTML = menu["day"];
    document.getElementById("day-title-a").href = menu["url"];
    document.getElementById("day-title-b").innerHTML = menu["day"];
    document.getElementById("day-title-b").href = menu["url"];

    // Lunch
    document.getElementById("lunch-1a").innerHTML = menu["lunch"]["p1"];
    document.getElementById("lunch-1b").innerHTML = menu["lunch"]["p1"];

    if (menu["lunch"]["p2"] != null) {
        document.getElementById("lunch-2a").style.display = 'block';
        document.getElementById("lunch-2a").innerHTML = menu["lunch"]["p2"];

        document.getElementById("lunch-2b").style.display = 'block';
        document.getElementById("lunch-2b").innerHTML = menu["lunch"]["p2"];
    } else {
        document.getElementById("lunch-2a").style.display = 'none';
        document.getElementById("lunch-2b").style.display = 'none';
    }

    // Dinner
    document.getElementById("dinner-1a").innerHTML = menu["dinner"]["p1"];
    document.getElementById("dinner-1b").innerHTML = menu["dinner"]["p1"];

    if (menu["dinner"]["p2"] != null) {
        document.getElementById("dinner-2a").style.display = 'block';
        document.getElementById("dinner-2a").innerHTML = menu["dinner"]["p2"];

        document.getElementById("dinner-2b").style.display = 'block';
        document.getElementById("dinner-2b").innerHTML = menu["dinner"]["p2"];
    } else {
        document.getElementById("dinner-2a").style.display = 'none';
        document.getElementById("dinner-2b").style.display = 'none';
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

tomorrow = function () {
    date_viewed.setDate(date_viewed.getDate() + 1);
    update_interface();
    update_buttons();
    console.log(date_viewed.print());
}

yesterday = function () {
    date_viewed.setDate(date_viewed.getDate() - 1);
    update_interface();
    update_buttons();
    console.log(date_viewed.print());
}

Date.prototype.print = function () {
    var year = this.getFullYear();
    var month = this.getMonth() + 1;
    var day = this.getDate();

    if (month < 10) {
        month = "0" + month;
    }
    month = "" + month;

    if (day < 10) {
        day = "0" + day;
    }
    day = "" + day;

    return parseInt(year + month + day);
}

function get(name) {
    if (name == '') return false;
    queryDict = {};
    queryDict[name] = false;
    location.search.substr(1).split('&').forEach(function (item) {
        queryDict[item.split('=')[0]] = true
    })

    return queryDict[name];
}

//window.onload = fetch_menus;
window.onload = update_interface;
document.getElementById("next").onclick = tomorrow;
document.getElementById("all").onclick = function () { window.location = '/menus' };
document.getElementById("previous").onclick = yesterday;
