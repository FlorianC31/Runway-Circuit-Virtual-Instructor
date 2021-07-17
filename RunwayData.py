import sqlite3
import param
from CoordCalc import distance, new_point, convert_coord, bearing
from math import cos, sin, radians


class LocalCircuit:
    def __init__(self, db_path, circuit_input_data):
        self.connexion = sqlite3.connect(db_path)
        self.cursor = self.connexion.cursor()
        self.airport_ident = circuit_input_data['airport']
        self.rwy_ident = circuit_input_data['rwy']
        self.side = circuit_input_data['side']

        self.airport_id = None
        self.mag_var = None
        self.airport_alt = None
        self.airport_pos = None

        self.runway_end_id = None
        self.heading_mag = None
        self.heading_true = None
        self.heading_db = None
        self.pos = None
        self.offset_threshold = None
        self.papi_pitch = None
        self.length = None
        self.end_pos = None
        self.altitude = None
        self.pattern_altitude = None
        self.d_target = None
        self.target = None

        self.get_airport_data()
        self.get_rwy_data()

    def get_airport_data(self):
        request = "SELECT airport_id, mag_var, altitude, lonx, laty FROM airport WHERE ident='" + \
                  self.airport_ident + "'"
        self.cursor.execute(request)
        result = self.cursor.fetchone()
        self.airport_id = result[0]
        self.mag_var = result[1]
        self.airport_alt = result[2]
        self.airport_pos = (result[3], result[4])

    def get_rwy_data(self):
        request = "SELECT runway_end_id, heading, lonx, laty, offset_threshold, left_vasi_pitch, right_vasi_pitch \
                    FROM runway_end AS A \
                    WHERE name='" + self.rwy_ident + "' AND ( \
                        (SELECT primary_end_id from runway AS B \
                        WHERE B.airport_id=" + str(self.airport_id) + " and B.primary_end_id=A.runway_end_id) \
                    OR \
                        (SELECT secondary_end_id from runway AS B \
                        WHERE B.airport_id=" + str(self.airport_id) + " and B.secondary_end_id=A.runway_end_id) \
                    )"

        self.cursor.execute(request)
        rwy_end_data = self.cursor.fetchone()
        if not rwy_end_data:
            return None

        self.runway_end_id = rwy_end_data[0]
        self.heading_db = rwy_end_data[1]
        self.pos = (rwy_end_data[2], rwy_end_data[3])
        self.offset_threshold = rwy_end_data[4]

        if rwy_end_data[5]:
            self.papi_pitch = rwy_end_data[5]
        elif rwy_end_data[6]:
            self.papi_pitch = rwy_end_data[6]
        else:
            self.papi_pitch = None

        request = "SELECT length, secondary_lonx, secondary_laty, altitude, pattern_altitude \
                    FROM runway WHERE primary_end_id = " + str(self.runway_end_id)
        self.cursor.execute(request)
        rwy_data = self.cursor.fetchone()
        if not rwy_data:
            request = "SELECT length, primary_lonx, primary_laty, altitude, pattern_altitude \
                    FROM runway WHERE secondary_end_id = " + str(self.runway_end_id)
            self.cursor.execute(request)
            rwy_data = self.cursor.fetchone()

        self.length = rwy_data[0] - self.offset_threshold
        self.end_pos = (rwy_data[1], rwy_data[2])
        self.altitude = rwy_data[3]
        self.pattern_altitude = rwy_data[4]
        self.heading_true = bearing(self.pos, self.end_pos)
        self.heading_mag = self.heading_true + self.mag_var

        # ref: https://www.sia.aviation-civile.gouv.fr/pub/media/reglementation/file/c/h/chea_a_01_v2.pdf (tableau 1.3)
        if self.length < 800 * param.METER2FEET:
            self.d_target = 150 * param.METER2FEET
        elif self.length < 1200 * param.METER2FEET:
            self.d_target = 250 * param.METER2FEET
        elif self.length < 2400 * param.METER2FEET:
            self.d_target = 300 * param.METER2FEET
        else:
            self.d_target = 400 * param.METER2FEET

        target_dist = self.d_target + self.offset_threshold

        self.target = new_point(self.pos, self.heading_true, target_dist)

    def print_rwy_data(self):
        piste_fin = new_point(self.pos, self.heading_mag, self.length + self.offset_threshold)
        print("check_distance_end", distance(self.end_pos, piste_fin), 'm')
        print('PAPI', self.papi_pitch)

        print(convert_coord(self.target))
        print(self.pos)

    def local_brg(self, point):
        brg = bearing(self.pos, point, True)
        brg -= radians(self.heading_true)
        return brg

    def local_coord(self, point):
        brg = self.local_brg(point)

        d = distance(self.pos, point, 'NM')
        x = - d * cos(brg)
        y = - d * sin(brg)
        if self.side == "LHS":
            y *= -1
        return x, y

    def get_descend_vs(self, speed):
        speed_fpm = speed / 60 * param.NM2METER * param.METER2FEET
        return -speed_fpm * sin(radians(self.papi_pitch))


if __name__ == "__main__":
    circuit = LocalCircuit(param.DB_PATH, param.CIRCUIT)
    # print(database.get_airport_id(AIRPORT))
    # print(database.get_mag_var(AIRPORT))
    # print(database.get_airport_coord(AIRPORT))
    # circuit.print_rwy_data()

    # pt_test = (1.269572222222222, 43.4504667)
    # print(circuit.local_coord(pt_test))
    # print(circuit.get_descend_vs(65), 'fpm')

    print('True heading', circuit.heading_true)
    print('Mag heading', circuit.heading_mag)
    print('Var mag', circuit.mag_var)
    print('Check', circuit.heading_true + circuit.mag_var)
