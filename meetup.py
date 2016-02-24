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

    @botcmd(split_args_with=None)
    def meetup_next(self, mess, args):
        """TODO"""
        if len(args) == 0:
            return 'Which MeetUp group would you like to query?'

        conn = client.HTTPSConnection(MEETUP_API_HOST)
        conn.request("GET", "/{name}/events".format(name=args[0]))
        r = conn.getresponse()

        if r.status == 404:
            return 'No MeetUp group found with this name.'

        if r.status != 200:
            return 'Oops, something went wrong.'

        res = json.loads(r.read().decode())
        return self.format_events(res)

    @staticmethod
    def datetimeformat(timestamp):
        return datetime.fromtimestamp(timestamp/1000).strftime('%d/%m/%Y')

    @staticmethod
    def format_events(results):
        env = Environment()
        env.filters['datetimeformat'] = MeetUpPlugin.datetimeformat

        EVENTS_TEMPLATE = env.from_string("""{% if results %}Next events for {{results[0].group.name}}:
{% for e in results%}[{{e.time|datetimeformat}}] \
"{{e.name}}" at {{e.venue.name}} - \
{{e.venue.city}} ({{e.link}})
{% endfor %}{% else%}No upcoming events.{% endif %}
""")
        return EVENTS_TEMPLATE.render({"results": results})
