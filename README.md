# err-meetup - meetup.com plugin for Err

[![Build Status](https://travis-ci.org/Djiit/err-meetup.svg?branch=master)](https://travis-ci.org/Djiit/err-meetup) [![Coverage Status](https://coveralls.io/repos/github/Djiit/err-meetup/badge.svg?branch=master)](https://coveralls.io/github/Djiit/err-meetup?branch=master)

Err-meetup is a plugin for [Err](https://github.com/gbin/err) that allows you to interact with [meetup.com](http://meetup.com).

## Features

* List upcoming events of a group.
* Poll new events from a user-defined watchlist and announce them.
* Add / remove groups to the meetup watchlist.

Have an idea ? Open an [issue](https://github.com/Djiit/err-meetup/issues) or send me a [Pull Request](https://github.com/Djiit/err-meetup/pulls).

## Usage

### Installation

As admin of an err chatbot, send the following command over XMPP:

```
!install git://github.com/Djiit/err-meetup.git
```

### Commands

Use `!help MeetUp` to see the available commands and their explanation.

## Configuration

Send configuration commands through chat message to this plugins as in :

```
!config MeetUp {'CHATROOMS': ()}
```
