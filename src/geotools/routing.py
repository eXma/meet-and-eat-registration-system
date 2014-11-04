import httplib
import json
import urllib

from cfg import config


class MapPoint(object):
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def as_route_target(self):
        return "%s,%s" % (self.lat, self.lng)

    @staticmethod
    def from_team(team):
        location = team.location
        return MapPoint(location.lat, location.lon)


class Router(object):
    def __init__(self):
        self._connection = None

    def _init_connection(self):
        self._connection = httplib.HTTPConnection("open.mapquestapi.com")

    @property
    def connection(self):
        if self._connection is None:
            self._init_connection()
        return self._connection

    def route(self, from_map_point, to_map_point):
        """

        :type from_map_point: MapPoint
        :type to_map_point: MapPoint
        """
        param_dict = {"outFormat": "json",
                      "routeType": "pedestrian",
                      "timeType": 1,
                      "enhancedNarrative": "false",
                      "locale": "de_DE",
                      "unit": "k",
                      "narrativeType": "none",
                      "rivingStyle": 2,
                      "highwayEfficiency": "21.0",
                      "from": from_map_point.as_route_target(),
                      "to": to_map_point.as_route_target(),
                      "key": config.MAPQUEST_KEY}

        params = urllib.urlencode(param_dict)

        url = "/directions/v1/route?%s" % (params)
        self.connection.request("GET", url)

        response = self._connection.getresponse()
        if response.status != 200:
            raise Exception("Query not successful: %s" % url)

        data = response.read()
        parsed = json.loads(data)

        if not isinstance(parsed, dict):
            raise Exception("No list returned: %s" % url)

        if "route" not in parsed:
            raise Exception("No result found: %s" % url)

        return Route(parsed["route"])

    def cleanup(self):
        self.connection.close()

    def __enter__(self):
        self._init_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class Route(object):
    def __init__(self, route_dict):
        self._route_dict = route_dict

    @property
    def start_location(self):
        return self._route_dict["locations"][self._route_dict["locationSequence"][0]]["latLng"]

    @property
    def end_location(self):
        return self._route_dict["locations"][self._route_dict["locationSequence"][1]]["latLng"]

    @property
    def openroute_link(self):
        base = "http://openrouteservice.org/index.php?start=%(start)s&end=%(end)s&pref=Pedestrian&lang=de"
        return base % {"start": "%s,%s" % (self.start_location["lng"], self.start_location["lat"]),
                       "end": "%s,%s" % (self.end_location["lng"], self.end_location["lat"])}

    def __repr__(self):
        return "Route[%s --> %s]: %s" % (self.start_location, self.end_location, self.distance)

    def __getattr__(self, item):
        if item != "_route_dict" and item in self._route_dict:
            return self._route_dict[item]
        raise AttributeError, item
