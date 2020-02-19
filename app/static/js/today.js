// Global menus variables
var dateViewed = new Date();
const days = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];

// Add loader
document.getElementById("N/A").style.display = "none";
document.getElementById("lunch").style.display = "none";
document.getElementById("dinner").style.display = "none";

function fetchMenus() {
    var force = get('force') || get('f')
    console.log('fetch with force=' + force);

    var url = '/api/menus'
    if (force) url += '?force';

    fetch(url)
        .then(response => {
            return response.json()
        })
        .then(data => {
            menus = data;
            updateInterface()
        })
        .catch(err => {
            console.log(err)
        })
}

function getDayTitle() {
    var day = days[dateViewed.getDay()];
    return day + " " + dateViewed.getDate();
}

function updateInterface() {
    var ask = dateViewed.print();
    var menu = menus.find(menu => menu["id"] == ask);

    console.log('Updating interface using day=' + ask);
    console.log(menu);

    document.getElementById("loader").style.display = "none";

    if (menu == null) {
        document.getElementById("N/A").style.display = "block";
        document.getElementById("lunch").style.display = "none";
        document.getElementById("dinner").style.display = "none";

        document.getElementById("day-title-a").innerHTML = getDayTitle();
        document.getElementById("day-title-a").href = PRINCIPAL_URL;
        document.getElementById("day-title-b").innerHTML = getDayTitle();
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

    updateButtons();

}

function updateButtons() {
    var yesterday = new Date();
    var tomorrow = new Date();

    yesterday.setDate(dateViewed.getDate() - 1);
    tomorrow.setDate(dateViewed.getDate() + 1);

    var yesterdayMenu = menus.find(menu => menu["id"] == yesterday.print());
    var tomorrowMenu = menus.find(menu => menu["id"] == tomorrow.print());

    if (yesterdayMenu == null) {
        document.getElementById("previous").disabled = true;
    } else {
        document.getElementById("previous").disabled = false;
    }

    if (tomorrowMenu == null) {
        document.getElementById("next").disabled = true;
    } else {
        document.getElementById("next").disabled = false;
    }
}

tomorrow = function () {
    dateViewed.setDate(dateViewed.getDate() + 1);
    updateInterface();
    updateButtons();
    console.log("Changed day to tomorrow (" + dateViewed.print() + ")");
}

yesterday = function () {
    dateViewed.setDate(dateViewed.getDate() - 1);
    updateInterface();
    updateButtons();
    console.log("Changed day to yesterday (" + dateViewed.print() + ")");
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

//window.onload = fetchMenus;
window.onload = updateInterface;
document.getElementById("next").onclick = tomorrow;
document.getElementById("all").onclick = function () { window.location.href = '/menus' };
document.getElementById("previous").onclick = yesterday;



// CLICK DETECTION
var xDown = null;
var yDown = null;
var lastTouch = new Date();

// If true, a middle click will auto-click in the middle button (redirect to /menus)
var enableMiddleClick = false;

// Calculate width
function updateWindowWidth() {
    newWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    if (newWidth == width)
        return;

    width = newWidth;
    console.log("Calculated width: " + width);
}
width = 0;
updateWindowWidth();

// Events listeners
document.addEventListener('touchstart', handleTouchStart, false);
document.addEventListener("click", handleClick);

// Handlers
function handleClick(e) {
    currentTime = new Date();
    if (currentTime - lastTouch < 750)
        return;

    updateWindowWidth();
    let cursorX = e.pageX * 100 / width;
    if (cursorX == 0)
        return;

    console.log("Click detected on PC: " + cursorX.toFixed(2) + "%");
    return clickDetected(cursorX);
}

function getTouches(evt) {
    return evt.touches || evt.originalEvent.touches;
}

function handleTouchStart(evt) {
    updateWindowWidth();
    const firstTouch = getTouches(evt)[0];
    cursorX = firstTouch.clientX * 100 / width;

    console.log("Detected Touch: " + cursorX.toFixed(2) + "%");
    lastTouch = new Date();
    return clickDetected(cursorX);
};


function clickDetected(cursorXPercentage) {
    let prevLeft = document.getElementById("previous").getBoundingClientRect()["left"] * 100 / width;
    let prevWidth = document.getElementById("previous").getBoundingClientRect()["width"] * 100 / width;
    let allWidth = document.getElementById("all").getBoundingClientRect()["width"] * 100 / width;

    let x = (50 - prevLeft - prevWidth - allWidth / 2) / 2;
    let centerDiff = allWidth / 2 + x;

    let rightMargin = 50 + centerDiff;
    let leftMargin = 50 - centerDiff;

    if (cursorXPercentage > rightMargin)
        return clickNext();
    if (cursorXPercentage < leftMargin)
        return clickPrevious();

    if (enableMiddleClick)
        return clickAll();
}

function clickPrevious() {
    console.log("Autoclicking left button (previous)");
    document.getElementById("previous").click();
}

function clickNext() {
    console.log("Autoclicking right button (next)");
    document.getElementById("next").click();
}

function clickAll() {
    console.log("Autoclicking middle button (all)");
    document.getElementById("all").click();
}
