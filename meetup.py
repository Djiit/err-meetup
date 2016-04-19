# coding: utf-8
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from datetime import datetime
from itertools import chain
import json
try:
    from http import client
except ImportError:
    import httplib as client

from jinja2 import Environment
from errbot import BotPlugin, botcmd


MEETUP_API_HOST = 'api.meetup.com'
POLL_INTERVAL = 3600
CONFIG_TEMPLATE = {'CHATROOMS': ()}


class MeetUpPlugin(BotPlugin):
    """Basic Err integration with meetup.com"""

    min_err_version = '3.2.3'
    # max_err_version = '3.3.0'

    def get_configuration_template(self):
        return CONFIG_TEMPLATE

    def configure(self, configuration):
        if configuration is not None and configuration != {}:
            config = dict(chain(CONFIG_TEMPLATE.items(),
                                configuration.items()))
        else:
            config = CONFIG_TEMPLATE
        super().configure(config)
        return

    def activate(self):
        super().activate()
        self.start_poller(POLL_INTERVAL, self.poll_events)
        self.init_store('watchlist', [])
        return

    def init_store(self, key, default_value):
        """Boostrap the internal storage with default values"""
        if key not in self:
            self[key] = default_value
        return

    def broadcast(self, msg):
        """Broadcast a message to all elligible chatrooms."""
        chatrooms = (self.config['CHATROOMS']
                     if self.config['CHATROOMS']
                     else self.bot_config.CHATROOM_PRESENCE)

        for room in chatrooms:
            self.send(self.build_identifier(room), msg)
        return

    def poll_events(self):
        """Poll upcoming events for group in the watchlist."""
        print(self['watchlist'])
        try:
            watchlist = self['watchlist']
            for i, group in enumerate(watchlist):
                status, events = self.request_events(group['name'])

                if status == 404:
                    self.log.warning('No MeetUp group found with this name.')
                    return
                if status != 200:
                    self.log.warning('Oops, something went wrong.')
                    return

                for event in events:
                    if event['id'] not in group['events']:
                        watchlist[i]['events'] += [event['id']]
                        self.broadcast('New meetup !\n{0}'.format(
                            self.format_event(event)))
            self['watchlist'] = watchlist
        except AttributeError:
            self['watchlist'] = []
        return

    @botcmd(split_args_with=None)
    def meetup_next(self, mess, args):
        """Fetch the upcoming events for a from meetup.com."""
        if len(args) == 0:
            return 'Which MeetUp group would you like to query?'

        status, events = self.request_events(args[0])

        if status == 404:
            return 'No MeetUp group found with this name.'

        if status != 200:
            return 'Oops, something went wrong.'

        if len(events) == 0:
            return 'No upcoming events.'

        return '\n'.join([self.format_event(e) for e in events])

    @botcmd(split_args_with=None)
    def meetup_watch(self, mess, args):
        """Add a group to the watchlist."""
        if len(args) == 0:
            return 'Which MeetUp group would you add to the watchlist?'

        if args[0] in [g['name'] for g in self['watchlist']]:
            return 'This group is already in the watchlist.'

        # we might need a simple check here : does the group exist ?
        self['watchlist'] += [{'name': args[0], 'events': []}]

        return 'Watchlist updated : {0}'.format(
            ', '.join([e['name'] for e in self['watchlist']]))

    @botcmd(split_args_with=None)
    def meetup_unwatch(self, mess, args):
        """Remove a group from the watchlist."""
        if len(args) == 0:
            return 'Which MeetUp group would you remove from the watchlist?'

        if args[0] not in [g['name'] for g in self['watchlist']]:
            return 'This group is not in the watchlist.'

        self['watchlist'] = [g for g in self['watchlist']
                             if g['name'] != args[0]]

        if not self['watchlist']:
            return 'Watchlist is now empty.'

        return 'Watchlist updated : {0}'.format(
            ', '.join([e['name'] for e in self['watchlist']]))

    @botcmd(split_args_with=None)
    def meetup_list(self, mess, args):
        """Display the current watchlist."""
        if not self['watchlist']:
            return 'Watchlist is empty.'
        return ('Currently watched MeetUp groups:\n' +
                ', '.join([e['name'] for e in self['watchlist']]))

    @botcmd(split_args_with=None)
    def meetup_fetch(self, mess, args):
        """Poll meetup.com manually for new incoming meetups."""
        self.poll_events()

    @staticmethod
    def request_events(group_name):
        """Query the meetup.com Events API v3. """
        conn = client.HTTPSConnection(MEETUP_API_HOST)
        conn.request("GET", "/{name}/events".format(name=group_name))
        r = conn.getresponse()
        return r.status, json.loads(r.read().decode())

    @staticmethod
    def datetimeformat(timestamp):
        """Jinja filter for date formating."""
        return datetime.fromtimestamp(timestamp/1000).strftime('%d/%m/%Y')

    @staticmethod
    def format_event(event):
        """Format event data."""
        env = Environment()
        env.filters['datetimeformat'] = MeetUpPlugin.datetimeformat
        EVENTS_TEMPLATE = env.from_string("""[{{e.time|datetimeformat}}] \
"{{e.name}}" at {{e.venue.name}} - {{e.venue.city}} ({{e.link}})""")
        return EVENTS_TEMPLATE.render({"e": event})
