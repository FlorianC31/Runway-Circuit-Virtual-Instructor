import param
from SimConnect import *
from math import degrees, tan, radians
from time import sleep


class SimConnection:
    def __init__(self):
        sim_connection = None
        fs_launched = False

        # Create SimConnect link
        while not fs_launched:
            try:
                sim_connection = SimConnect()
                fs_launched = True
                print("Connection established")
            except ConnectionError:
                print("FS non lancé")
                sleep(5)

        self.sim_connexion = SimConnect()

        # Note the default _time is 2000 to be refreshed every 2 seconds
        self.aq = AircraftRequests(sim_connection, _time=0)

        # Use _time=ms where ms is the time in milliseconds to cache the data.
        # Setting ms to 0 will disable data caching and always pull new data from the sim.
        # There is still a timeout of 4 tries with a 10ms delay between checks.
        # If no data is received in 40ms the value will be set to None
        # Each request can be fine tuned by setting the time param.

    def get_true_altitude(self):
        return self.aq.get("PLANE_ALTITUDE")

    def get_position(self):
        lat = self.aq.get("PLANE_LATITUDE")
        long = self.aq.get("PLANE_LONGITUDE")
        return long, lat

    def get_ground_speed(self):
        return self.aq.get("GROUND_VELOCITY")

    def get_ias(self):
        return self.aq.get("AIRSPEED_INDICATED")

    def get_tas(self):
        return self.aq.get("AIRSPEED_TRUE")

    def get_vs(self):
        return self.aq.get("VERTICAL_SPEED")

    def get_indicated_alt(self):
        return self.aq.get("INDICATED_ALTITUDE")

    def get_true_alt(self):
        return self.aq.get("PLANE_ALTITUDE")

    def is_on_ground(self):
        return self.aq.get("SIM_ON_GROUND")

    def get_hdg_true(self):
        return degrees(self.aq.get("PLANE_HEADING_DEGREES_TRUE"))

    def get_hdg_mag(self):
        return degrees(self.aq.get("PLANE_HEADING_DEGREES_MAGNETIC"))

    def show_msg(self, msg):
        self.sim_connexion.sendText(str(msg), 1)
        print(str(msg))

    def get_freq(self):
        return self.aq.get("COM_ACTIVE_FREQUENCY:1")

    def is_ivao_unicom(self):
        if self.aq.get("COM_ACTIVE_FREQUENCY:1") is None:
            return False
        return 122.799 < self.aq.get("COM_ACTIVE_FREQUENCY:1") < 122.801

    def exit(self):
        self.sim_connexion.exit()

    def turn_dist(self, approach_speed=True, safe=False):
        g = param.G / param.NM2METER
        if safe:
            angle = param.BANK_ANGLE_SAFE / 1.5
        else:
            angle = param.BANK_ANGLE / 1.5

        if approach_speed:
            speed = param.AIRCRAFT['Vapp'] / 3600
        else:
            speed = self.get_ground_speed() / 3600

        d = pow(speed, 2) / (tan(radians(angle)) * g)
        d += param.T_LAG * speed

        return d
