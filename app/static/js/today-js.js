function fetch_menus() {
    fetch('/api/menus')
    .then(response => {
        return response.json()
    })
    .then(data => {
        console.log(data)
    })
    .catch(err => {
        console.log(err)
    })
}

window.onload = fetch_menus;