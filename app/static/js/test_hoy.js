$(document).ready( function () {
        console.log("ready");
        $.getJSON("/api/menus")
            .done(function(data) {
                console.log("done 1");
                console.log(data);
                console.log("done 2");
        })
        console.log("done 3");
    }
);