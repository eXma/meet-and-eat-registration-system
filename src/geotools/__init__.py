from geotools.routing import Router


def simple_distance(point_a, point_b):
    with Router() as router:
        route = router.route(point_a, point_b)
        return route.distance


def openroute_link(map_points):
    base = "http://openrouteservice.org/index.php?start=%(start)s&end=%(end)s&%(via)spref=Pedestrian&lang=de"

    start = map_points[0]
    stop = map_points[-1]

    via = ""
    if len(map_points) > 2:
        vias = []
        for point in map_points[1:-1]:
            vias.append("%s,%s" % (point.lng, point.lat))
        via = "via=%s%%20&" % "%20".join(vias)

    return base % {"start": "%s,%s" % (start.lng, start.lat),
                   "end": "%s,%s" % (stop.lng, stop.lat),
                   "via": via}