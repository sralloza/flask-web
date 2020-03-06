# Sites available
**Note:** Right now, the default page `/` redirects to `/hoy`.

## API sites
* `/api/menus/add` - Add a new menu using API.
* `/api/menus` - Returns all the menus as json. Part of the API.

## Menus sites
* *Today's menu sites*:
  * `/hoy`: only one menu is showed at the same time (unlike `/menus`). Also works with `/h`.
    * Accepts only one url argument, `update`. If it's present, the database will be updated.
  * `/hoy/update`: Redirects to `/hoy?update`, since that's how the database update is processed now.

* *Manually edit menus*
  * `/add`: allows the user to add a new menu using a graphical interface.
  * `/del`: allow the user to remove an old menu using a graphical interface.

* *List all menus*
  * `/menus`: shows the menus as a table. Also works with `/new-menus`, `/new_menus` and `/m`. Accepts 2 url arguments:
    * `all`: shows every menu in the table.
    * `beta`: uses `datatables` to add more advanced functions like filters and sorters, with an improved table view.

    **If both arguments (`all` and `beta`) are present in the url, `beta` argument will prevail `all` argument, because
    the `beta` view shows `all` menus, and thus includes the all argument.**
  * `/menus/update`: shows a list of menus, updating the database in the process.
    Notes:
    * After updating the database, the user is redirected to `/menus`.

## Other sites
* `/notifications`: also works with `/notificaciones`, `/alerts` and `/alertas`. Designed for testing the notification sytem.
* `/favicon.ico`: returns the favicon.
* `/version`: shows the version. Also works with `/v`,
* `/feedback`: shows some info to send feedback.
* `/source`: redirects to the most recent source of menus data. Also works with `/s`.
* `/bootstrap/static/<filename>`: returns bootstrap's files.
* `/static/<filename>`: returns static files, like `css` and `javascript`.
