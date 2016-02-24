# coding: utf-8
import meetup


class TestMeetUpPlugin(object):
    extra_plugin_dir = '.'


class TestMeetUpPluginStaticMethods(object):

    def test_format_events(self):
        data = [{
            "created": 1448071373000,
            "duration": 10800000,
            "group": {
                "created": 1447912923000,
                "name": "Dummy Events",
                "id": 19135877,
                "join_mode": "open",
                "lat": 48.86000061035156,
                "lon": 2.3399999141693115,
                "urlname": "Dummy_Events",
                "who": "Guild Members"
                },
            "id": "226921105",
            "link": "http://www.meetup.com/Dummy_Events/events/123456/",
            "name": "Dummy Events #0",
            "status": "upcoming",
            "time": 1458750600000,
            "updated": 1455112512000,
            "utc_offset": 3600000,
            "yes_rsvp_count": 99,
            "waitlist_count": 0,
            "description": "dummy",
            "venue": {
                "id": 24290784,
                "name": "Dummy Cafe",
                "lat": 48.86763000488281,
                "lon": 2.3495399951934814,
                "repinned": False,
                "address_1": "0",
                "city": "Paris",
                "country": "fr",
                "localized_country_name": "France"
            },
            "how_to_find_us": "Dummy Cafe",
            "visibility": "public"
        }]
        result = meetup.MeetUpPlugin.format_events(data)
        assert result == """Next events for Dummy Events:
[23/03/2016] "Dummy Events #0" at Dummy Cafe - Paris \
(http://www.meetup.com/Dummy_Events/events/123456/)
"""

    def test_format_events_empty_list(self):
        data = []
        result = meetup.MeetUpPlugin.format_events(data)
        assert result == """No upcoming events."""




