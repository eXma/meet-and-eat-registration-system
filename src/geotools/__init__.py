from geotools.routing import Router


def simple_distance(point_a, point_b):
    with Router() as router:
        route = router.route(point_a, point_b)
        return route.distance