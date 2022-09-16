This package allows you to interface with [Horse Reality](https://horsereality.com) pages on a read-only basis using user account credentials. It handles authentication on your behalf and provides a small collection of models for easier interfacing.

## Meta

This package was made for the [Realtools API](https://github.com/hr-tools/api) but it is provided as a separate package here. It is not available for download on PyPI; pip is able to install directly from GitHub:

```
python3 -m pip install git+https://github.com/hr-tools/horsereality
```

Or, on Windows:

```
py -m pip install git+https://github.com/hr-tools/horsereality
```

## Example

This example showcases the `get_horse` client method as well as some features of the `Horse` model that it returns.

```py3
import asyncio
import horsereality

hr = horsereality.Client('...', '...')

async def show_horse(lifenumber: int):
    await hr.verify()
    # In reality you shouldn't verify every time. The package will attempt to
    # use its cached remembrance token to re-login if need be.

    horse = await hr.get_horse(lifenumber)
    print(horse.name)
    # 'Rear Window'
    print(horse.sex)
    # 'stallion'
    print(horse.birthdate_date)
    # datetime.date(2021, 12, 9)

asyncio.run(show_horse(7187887))
```

## Mini API Reference

The featureset is fairly limited at this time, developed primarily according to the needs of the Realtools API.

### `horsereality.Client(remember_cookie_name: str, remember_cookie_value: str, *, auto_rollover: bool = False)`

This is the main client class that your session will live in an instance of, and that with external calls will usually be made. In order to create an instance of this class, you will need to grab the value of the cookie starting with `remember_web_` that your browser is sent upon logging in to Horse Reality with the "remember me" option enabled (the `Set-Cookie` header in the response of POST /login). This "remember" cookie is typically set to expire after 5 years - 1 day, so you should be safe from replacing it often.

#### Rollover

Every day at 0:00 in the Netherlands, Horse Reality requires the client to "roll over" their account. The module allows this to be done manually via a call to [`Client.rollover`](#await-rollover), but it will be done automatically (as soon as necessary) if the `auto_rollover` parameter is provided as `True` while constructing the `Client`. By default, however, it is disabled.

#### Methods

##### `await verify()`

Verify the data provided to the `Client`. This method 'primes' the client and is required for any pages to be readable. You should only have to call this once in your application's lifetime.

##### `await get_horse(lifenumber: int)`

Fetch a horse from Horse Reality by its lifenumber. Returns a [`Horse`](#horserealityhorse).

##### `await rollover()`

Complete the daily rollover required every day after 0:00 CET/CEST (i.e. the current timezone in the Netherlands depending on DST).

### `horsereality.Horse`

#### Attributes

* `lifenumber` `int` - The horse's lifenumber.
* `name` `str` - The horse's name.
* `sex` `str` - The horse's sex. Could be one of `stallion`, `gelding`, or `mare`.
* `breed` `str` - The horse's breed, lowercased and underscored (`Brumby Horse` -> `brumby_horse`)
* `raw_breed` `str` - The raw value of `breed` (not lowercased and underscored)
* `age` `str` - The horse's age as a long-form human-friendly string
* `birthdate` `str` - The horse's birthdate
* `birthdate_date` `datetime.date` - `birthdate` as a `datetime.date`
* `height` `str` - The horse's height as a long-form human-friendly string
* `location` `str` - The horse's continent
* `owner` `str` - The name of the horse's owner
* `registry` `str` - The name of the horse's registry
* `predicates` `str` - The horse's predicates

The following attributes are metadata for the page that `lifenumber` refers to rather than the horse itself:

* `looking_at` `Optional[str]` - The horse that the page belongs to. Could be one of `'dam'`, `'foal'`, or `None`.
* `adult_layers` `List[Layer]` - The layers of the adult on the page.
* `foal_layers` `List[Layer]` - The layers of the foal on the page.
* `layers` `List[Layer]` - The layers of whichever horse the page belongs to.
* `foal_lifenumber` `Optional[int]` - The lifenumber of the foal on the page, if it exists and the page does not already belong to it.

#### Methods

##### `is_foal()`

Whether or not the page belongs to a foal. Returns a `bool`.

##### `await fetch_foal()`

Fetches the dam's foal. If `foal_lifenumber` is not `None`, returns a [`Horse`](#horserealityhorse), else raises a `ValueError`.

### Exceptions

All library exceptions are subclasses of `horsereality.HorseRealityException`.

#### `HTTPException`

A request failed.

#### `AuthenticationException`

Failed to authenticate with Horse Reality.

#### `PageAlertException`

Raised when a page is accessed successfully, but it displays an error message (e.g. https://www.horsereality.com/horses/0/).

#### `RolloverRequired`

Raised when a page could not be accessed because the client's account has not been rolled over (see also: [`Client.rollover`](#await-rollover)).

##### Attributes

* `url` `str` - The URL that the client attempted to access.
* `response` `aiohttp.ClientResponse` - The response from Horse Reality.
* `rollover_url` `str` - The qualified URL for the client to rollover at (https://v2.horsereality.com/daily-rollover?url=...), should the implementation prefer deferring to a human.
