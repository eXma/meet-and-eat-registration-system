from geotools.routing import Router


def simpleDistance(point_a, point_b):
    with Router() as router:
        route = router.route(point_a, point_b)
        return route.distance