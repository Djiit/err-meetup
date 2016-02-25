# coding: utf-8
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from datetime import datetime
import json
try:
    from http import client
except ImportError:
    import httplib as client

from jinja2 import Environment
from errbot import BotPlugin, botcmd


MEETUP_API_HOST = 'api.meetup.com'


class MeetUpPlugin(BotPlugin):
    """Basic Err integration with meetup.com"""

    min_err_version = '3.2.3'
    # max_err_version = '3.3.0'

    def activate(self):
        super().activate()
        self.start_poller(10, self.poll_events)  # DEV: 10=3600
        return

    def poll_events(self):
        """Poll upcoming events for group in the watchlist."""
        try:
            for group in self.watchlist:
                status, events = self.request_events(group['name'])

                if status == 404:
                    self.log.warning('No MeetUp group found with this name.')
                    return
                if status != 200:
                    self.log.warning('Oops, something went wrong.')
                    return

                for event in events:
                    if event['id'] not in group['events']:
                        for room in self.bot_config.CHATROOM_PRESENCE:
                            self.send(
                               room,
                               self.format_event(event),
                               message_type='groupchat')
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

        for event in events:
            yield self.format_event(event)
        return

    @botcmd(split_args_with=None)
    def meetup_watch(self, mess, args):
        """Add a group to the watchlist."""
        if args[0] in [g['name'] for g in self['watchlist']]:
            return 'This group is already in the watchlist.'

        # we might need a simple check here : does the group exist ?

        self['watchlist'].append({'name': args[0], 'events': []})

        return 'Watchlist updated : {0}'.format(self['watchlist'])

    @botcmd(split_args_with=None)
    def meetup_unwatch(self, mess, args):
        """Fetch the upcoming events for a from meetup.com."""
        if args[0] not in [g['name'] for g in self['watchlist']]:
            return 'This group is not in the watchlist.'

        self['watchlist'] = [g for g in self['watchlist']
                             if g['name'] != args[0]]

        return 'Watchlist updated : {0}'.format(self['watchlist'])

    @staticmethod
    def request_events(group_name):
        """ Fetch meetup.com Events v3 API endpoint. """
        conn = client.HTTPSConnection(MEETUP_API_HOST)
        conn.request("GET", "/{name}/events".format(name=group_name))
        r = conn.getresponse()
        return r.status, json.loads(r.read().decode())

    @staticmethod
    def datetimeformat(timestamp):
        return datetime.fromtimestamp(timestamp/1000).strftime('%d/%m/%Y')

    @staticmethod
    def format_event(event):
        env = Environment()
        env.filters['datetimeformat'] = MeetUpPlugin.datetimeformat
        self.log.debug
        EVENTS_TEMPLATE = env.from_string("""[{{e.time|datetimeformat}}] \
"{{e.name}}" at {{e.venue.name}} - {{e.venue.city}} ({{e.link}})""")
        return EVENTS_TEMPLATE.render({"e": event})
