from math import asin, sin, cos, sqrt, pow, radians, atan2, pi, degrees
import param


def distance(point_a, point_b, convert=None):

    phi1 = radians(point_a[1])
    phi2 = radians(point_b[1])
    land1 = radians(point_a[0])
    land2 = radians(point_b[0])

    delta_teta = 2 * asin(sqrt(pow(sin((phi2 - phi1)/2), 2) + cos(phi1) * cos(phi2) * pow(sin((land2 - land1) / 2), 2)))

    d = param.EARTH_RADIUS * delta_teta
    if convert == 'ft':
        d *= param.METER2FEET
    elif convert == 'NM':
        d /= param.NM2METER
    return d


def bearing(point_a, point_b, rad=False):
    lat1 = radians(point_a[1])
    lat2 = radians(point_b[1])
    lon1 = radians(point_a[0])
    lon2 = radians(point_b[0])

    brg = atan2(sin(lon2 - lon1) * cos(lat2), cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1)) + pi

    if rad:
        return brg_limit(brg)
    else:
        return brg_limit(degrees(brg + pi))


def resultante(pos):
    return sqrt(pow(pos[0], 2) + pow(pos[1], 2))


def brg_limit(brg, rad=False):

    if rad:
        if brg > pi:
            brg -= 2 * pi
        elif brg <= -pi:
            brg += 2 * pi
        return brg
    else:
        if brg > 360:
            brg -= 360
        elif brg <= 0:
            brg += 360
        return brg


def complement_brg(brg, rad=False):
    if rad:
        new_brg = brg + pi
        if new_brg > pi:
            new_brg -= 2 * pi
        return new_brg
    else:
        new_brg = brg + 180
        if new_brg > 360:
            new_brg -= 360
        return new_brg


def new_point(origin, cap, dist):

    lat1 = radians(origin[1])
    long1 = radians(origin[0])
    brg = radians(cap)
    d = dist / param.METER2FEET / 1000  # km
    er = param.EARTH_RADIUS / 1000  # km

    lat2 = asin(sin(lat1) * cos(d / er) + cos(lat1) * sin(d / er) * cos(brg))
    long2 = long1 + atan2(sin(brg) * sin(d / er) * cos(lat1), cos(d / er) - sin(lat1) * sin(lat2))

    return degrees(long2), degrees(lat2)


def decimal2angle(decimal):

    x = int(abs(decimal))
    y = int((abs(decimal) - x) * 60)
    z = round((abs(decimal) - x - y / 60) * 3600, 2)

    angle = str(x) + "° " + str(y) + "' " + str(z) + '" '

    return angle


def convert_coord(point):
    if point[0] > 0:
        ew = 'E'
    else:
        ew = 'W'

    if point[1] > 0:
        ns = 'N'
    else:
        ns = 'S'
    # print(decimal2angle(point[1]), decimal2angle(point[0]))
    return decimal2angle(point[1]) + ns + ', ' + decimal2angle(point[0]) + ew


if __name__ == "__main__":

    # pt1 = (0.2545, 51.8853)
    # pt2 = (2.5735, 49.0034)
    c1 = 108.55
    c2 = 32.44

    pt1 = (1.106231689453125, 43.00335693359375)
    pt2 = (1.100128173828125, 43.01219940185547)

    print('Distance', distance(pt1, pt2) / 1000)
    print('Bearing1', bearing(pt1, pt2))
    print('Bearing2', complement_brg(bearing(pt2, pt1)))

    # print(convert_coord(intersection(pt1, c1, pt2, c2)))
    # print(convert_coord(intersection2(pt1, c1, pt2, c2)))
    # print('----------------------')

    # intersect1 = intersection2(pt1, c1, pt2, c2)
    # print('----------------------')
    # intersect2 = intersection2(pt2, c2, pt1, c1)
    # print('----------------------')
    # print(bearing(pt1, intersect1))
    # print('----------------------')
    # print(bearing(pt1, intersect2))
