$(document).ready(function () {
    $('#menus_table').DataTable({
        // "ordering": false
        "order": [[0, "desc"]],
        "columns": [
            { "orderDataType": "date-dd-MMM-yyyy" },
            null,
            null,
            null,
            null
        ]
    });
    console.log('loaded');
}
);
