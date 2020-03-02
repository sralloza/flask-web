# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
* Added testing of all menus published until `March 1, 2020`.
* New argument for `get_menus_urls`: `request_all`. If True, it will return all menus urls.
* Add downloader class with retry control: `Downloader`

### Changed
* Changed test data storage system.
* Moved `get_last_menus_page` from `app.utils` to `app.menus.core.utils`.
* Make `get_last_menus_page` use `get_menus_urls` if it can't generate the last url.
* Rename `get_last_menus_page` to `get_last_menus_url`.

### Fixed
* Fixed some bugs with `cocktail` and `combined plates`.
* Fixed some bugs using semicolons instead of colons, like `comida;` instead of `comida:`

## [2.1.0] - 2020-02-20
### Added
* In `/hoy` endopoint, clicking in `All` button will allow the user to go back (click enable instead of HTTP redirect).
* Enabled use of keys and clicking in `/hoy` endpoint. Clicks on the left will auto-click `previous` button, and clicks on the right will auto-click `next` button. This can be done with keys `K` and `L`, respectively. Also, `left arrow` and `right arrow` work, too. `T` key will change the date view to today's date.
* Clicks on mobile browser are also supported.
* Add `/v` and `/version` urls to check current version.

### Changed
* Renamed `today-js.js` to `today.js`.
* Renamed `today-js.html` to `today.html`

### Fixed
* Fix Web Server Gateway Interface - `flaskapp.wsgi`

## [2.0.0] - 2020-02-17

### Added
* Add `url` attribute to alias database (`alias.json`).
* Add `url` attribute to `DailyMenu`.
* Add `url` argument to `BaseParser.process_text()`.
* Add `url` attribute to json representation of `DailyMenu`.
* Log final decition of updating database.

### Changed
* Use javascript to set the title's link in `/hoy` endpoint to the menu's url. If now menu is display (day not in the database), title's link is set to the principal menu * url.
* File `file-access.log` will not be created in linux (requests log are managed by Apache).
* Redirect `/hoy/reload` to `/hoy?force`.
* Changed logging format to include `threadName` and `module`.

### Fixed
* Fixed content parsing if between a meal is place a line sepparator (`\n`).
* Fixed content parsing if more than one space between words is used.
* Added more tests.

### Removed
* Removed backwards compatibility of table.
* Removed call to `get_last_menus_page()` in `/hoy` endpoint, so it loads far more quickly.

## [1.3.0] - 2020-02-01
### Added
* Add `TOKEN_FILE_PATH` config.
* New token system. All tokens written in `TOKEN_FILE_PATH` config will be accepted.

## [1.2.0] - 2020-01-31
### Changed
* Set web to work `OFFLINE`, because menus are no longer uploaded in text format but as images.
* `force` argument of `DailyMenusManager.load` only forces downloading, it can't force no downloading. `UpdateControl` can override it.
* Renamed data files to `.data` extension to avoid github detecting false html files.


### Fixed
* Add support to process `1 plato`, `2 plato` and `2o plato`, instead of the standards `1er plato` and `2º plato`.
* Add support to process dates without ending bracket, like `día: 25 de abril de 2020 (viernes`.
* Remove dots from any meal.
* Add complete menus processing tests.

## [1.1.1] - 2019-11-23
### Changed
* Deny access to `smtbot`, `nimbostradamus` and other bots.

## [1.1.0] - 2019-11-21

[Unreleased]: https://github.com/sralloza/flask-web/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/sralloza/flask-web/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/sralloza/flask-web/compare/v1.3.0...v2.0.0
[1.3.0]: https://github.com/sralloza/flask-web/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/sralloza/flask-web/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/sralloza/flask-web/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/sralloza/flask-web/releases/tag/v1.1.0
