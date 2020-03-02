# Test data
This data structure is designed to work automatically. If more test data is needed, just add more test files.
The file `data.py` will recognize and manage it.


# Test Data Structure

## filter_data
**TODO: improve testing**

### Inputs
Input files have words that appear in the real web (somewhat parsed), so `filter_data`
can remove the useless ones. Each line has a group.

### Outputs
Output files have words that are useful to the system (one group per line).


## HtmlParser.parse
**TODO: add tests for 2017 and 2018**

### Inputs
There are 3 folders (`pdf`, `photos` and `html`) to save inputs of each type. Additionaly, there is
a file at the same level as the folders named `urls.json` that states which url does each file come from.

Each file inside each folder is always named after the first menu stored in itself, using its date with the format `YYYY-MM-DD`, like `2020-02-29`.

`urls.json` consists of a dictionary of three keys (`pdf`, `photos` and `html`). Each key is associated with
another dictionary, whose keys are the test filenames (dates like `2020-02-29`) and the values are the
urls of each test file.

### Outputs
There is just one folder (`html`), because `pdf` and `photos` types does not produce any output. Its tests consists of just detecting the type.

## get_menus_urls
### Inputs
Each file represents the response of the menus server. It's named like `FIRST_DATE-LAST_DATE.html.data`, where `FIRST_DATE` is the least recent date which appears in the response and `LAST_DATE` is the most recent date which appears in the response.

### Outputs
Each file represents the urls parsed from each response of the server. They are named like `FIRST_DATE-LAST_DATE.json`. FIRST_DATE and LAST_DATE means the same as in [Inputs](#inputs-2)

### Invalid
Extra folder which contains just one file, `invalid-page.html.data`. It's the response of the menus server for a request of a non-existing page (index too big)

# Known errors
There are some errors in the web that can not be fixed with this software. Those error are listed here:

* Orthographic errors, like lack of accents.
* `November 6, 2017` is saved with the month set to October, so instead of Monday (real weekday) the system detects it as a Friday.
* Between `February 27, 2018` and `March 5, 2018` (both included) there is no data.
* Between `March 20, 2018` and `March 26, 2028` (both included) the web shows no data, but the web page exists. **It is skipped from tests.**
* Between `March 29, 2018` and `April 7, 2018` (both included) there is no data.
* `April 14, 2018` is saved with the year set to 2019, so instead of Saturday (real day) the system detects it as Sunday.
* `June 19, 2018` is not processed correctly because the day is given as DD/MM/YYYY, which is not the standard format. If the algorithm translates this date into the standard format, everything would colapse, because at the top of the page it's always place the menus' redaction date in that format. **It is skipped from tests**.
* Between `June 22, 2018` and `June 26, 2018` (both included) there is no data.
* `December 18, 2018` is saved with the month set to October, so instead of Tuesday (real weekday) the system detects it as Thursday.
* `December 19, 2018` is saved with the month set to October, so instead of Wednesday (real weekday) the system detects it as Friday.
* `December 20, 2018` is saved with the month set to October, so instead of Thursday (real weekday) the system detects it as Saturday.
* `December 21, 2018` is saved with the month set to October, so instead of Friday (real weekday) the system detects it as Sunday.
* `April 6, 2019` is saved with the month set to March, so instead of Saturday (real weekday) the system detects it as Wednesday.
* `April 7, 2019` is saved with the month set to March, so instead of Sunday (real weekday) the system detects it as Thursday.
* `April 13, 2019` is saved with the month set to March, so instead of Saturday (real weekday) the system detects it as Wednesday.
* In the week of `September 23, 2019` the url and the title states that the first date of the week is September 22, which is wrong.
* Between `November 4, 2019` and `November 17, 2019` (both included) there is no data.
