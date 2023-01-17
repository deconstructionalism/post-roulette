# Post Roulette

A simple, probably over-built `curses` app that loads and displays
post data from various social media data dumps so that a user can
jog thru and select posts to save in a local JSON DB.

## Purpose

The intent of this app was to create a clean way to look at one post at
a time, which I am using to write down posts that I find compelling or
relevant onto physical note cards for organization outside of this app.
The app also saves selected posts in a JSON DB which provides a digital
copy of saved posts.

## Requirements

- python (tested on `3.9.8`)
- poetry (tested on `1.1.13`)

## Setup

1. Run `poetry install` to install all dependencies.
2. Get a data dump for whichever social media platform you want. See
   [Raw Data](#raw-data) for more details on data shape.
3. Make sure that there is a config for the social media platform. See
   [Config](#config) for more details.

## Running

1. Run `poetry run roulette <social media config name>`.
2. Follow on screen instructions to jog thru or save/remove posts. Saved posts can
   be found in `./db/db.json`. See [Database](#database) for more details.

## Architecture

### Config

You define the config for loading and transforming a given social media platform
in `./post_roulette/config.py::source_configs`.

Each mapper is of the type `SourceConfig` as defined in `./post_roulette/types.py`
and should thus include the name of the social media platform, the associated
[mapper](#mappers) function, and the name of the
[associated data dump file](#raw-data) in `./data/`.

> NOTE: The key in `source_configs` is the name of the social media platform
> passed as a positional arg to `poetry run roulette`.

### Raw Data

Raw JSON post data from social media dumps is stored in `./data`. The dump should
be formatted as an JSON array with each item in the array corresponding to a post,
which is what most social media platforms provide.

### Mappers

Mappers are modules containing single functions located in `./post_roulette/mappers`.
The functions transform a row from a JSON data dump for a social media platform into
the appropriate shape for the app.

A mapper function should be of the type `MapRowToPost` as described in
`./post_roulette/types.py`.

### Database

This app uses `tinyDB` to manipulate a JSON database stored in `./db/db.json`.

There are two kinds of documents in the database: "cursors", and "posts". Document
schemas are not enforced by validation but their shape is given below.

Documents controllers are located in `./post_roulette/models`.

#### Cursor Documents

Cursor documents store the last index within the posts for a given social media
dump where a user took action. This allows for the user to resume sessions in
the same place they left off.

##### Cursor Schema

```json
{
  "source_name": str, // name of social media platform
  "value": int // last accessed index in posts from social media platform
}
```

#### Post Documents

Post documents are individual post data from a given social media dump that the
user decided to save via the UI. These posts have a stereotyped shape and
the raw data provided by a platform is mapped to this shape via the
[Mappers](#mappers) described below.

##### Post Schema

```json
{
  "source_name": str, // name of social media platform
  "index": int, // index of post in data dump from platform
  "content": str, // text content of post
  "datetime": str // human readable date time
}
```

## Remaining Chores

- write tests
- figure out how to transform Instagram data so that images can be OCR-ed into
  text data (probably out of scope for this app)
