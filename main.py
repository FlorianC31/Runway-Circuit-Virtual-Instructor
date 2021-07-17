import param
from time import sleep
from RunwayData import LocalCircuit
from CoordCalc import brg_limit
from SimConnectInterface import SimConnection


class CurrentCircuit (LocalCircuit):
    def __init__(self, db_path, circuit_input_data):
        LocalCircuit.__init__(self, db_path, circuit_input_data)
        self.phase = 10

        if param.CIRCUIT['side'] == "LHS":
            self.turn_side_msg = "Turn left in "
        else:
            self.turn_side_msg = "Turn right in "

        self.crosswind_dist = param.AIRCRAFT['Vinit_climb'] / 3600 * param.CROSSWIND_TIME

        self.max_crosswind_x = 500 / param.AIRCRAFT['Min_VS'] * param.AIRCRAFT['Max_climb_speed'] / 60 + self.length
        # time to climb to 500ft at min VS and max climb speed, + runway length

    def is_initial_climb(self, pos, brg, alt):
        alt_cond = 50 < alt < self.pattern_altitude + param.TOL_ALT  # above 50ft AAL and below patern alt + tolerance
        brg_cond = brg < param.TOL_ANG or brg >= 360 - param.TOL_ANG  # heading 360° more or less 45°
        pos_cond_x = pos[0] > 0  # In front of the runway
        pos_cond_y = 0 - param.TOL_DIS < pos[1] < 0 + param.TOL_DIS  # in the axis of the runway more or less tolerance
        if alt_cond and brg_cond and pos_cond_x and pos_cond_y:
            return True
        else:
            return False

    def is_crosswind(self, pos, brg, alt):
        alt_cond = self.pattern_altitude / 2 - param.TOL_ALT < alt < self.pattern_altitude + param.TOL_ALT
        brg_cond = 270 - param.TOL_ANG <= brg < 270 + param.TOL_ANG  # heading 270° more or less 45°
        pos_cond_x = 1.0 - param.TOL_DIS < pos[0] < self.max_crosswind_x + param.TOL_DIS
        pos_cond_y = 0.0 - param.TOL_DIS < pos[1] < 1.6 + param.TOL_DIS
        if alt_cond and brg_cond and pos_cond_x and pos_cond_y:
            return True
        else:
            return False

    def is_downwind(self, pos, brg, alt):
        alt_cond = self.pattern_altitude / 2 - param.TOL_ALT < alt < self.pattern_altitude + param.TOL_ALT
        brg_cond = 180 - param.TOL_ANG <= brg < 180 + param.TOL_ANG
        pos_cond_x = -1.6 - param.TOL_DIS < pos[0] < self.max_crosswind_x + param.TOL_DIS
        pos_cond_y = 1.0 - param.TOL_DIS < pos[1] < 1.6 + param.TOL_DIS
        if alt_cond and brg_cond and pos_cond_x and pos_cond_y:
            return True
        else:
            return False

    def is_base(self, pos, brg, alt):
        alt_cond = 0 + param.TOL_ALT < alt < self.pattern_altitude + param.TOL_ALT
        brg_cond = 90 - param.TOL_ANG <= brg < 90 + param.TOL_ANG
        pos_cond_x = -1.6 - param.TOL_DIS < pos[0] < 0
        pos_cond_y = 0.0 - param.TOL_DIS < pos[1] < 1.6 + param.TOL_DIS
        if alt_cond and brg_cond and pos_cond_x and pos_cond_y:
            return True
        else:
            return False

    def is_final(self, pos, brg, alt):
        alt_cond = alt < self.pattern_altitude + param.TOL_ALT
        brg_cond = brg < param.TOL_ANG or brg >= 360 - param.TOL_ANG  # heading 360° more or less 45°
        pos_cond_x = -1.6 - param.TOL_DIS < pos[0] < self.length / 2
        pos_cond_y = 0 - param.TOL_DIS < pos[1] < 0 + param.TOL_DIS  # in the axis of the runway more or less tolerance
        phase_cond = self.phase > 1
        print(alt_cond, brg_cond, pos_cond_x, pos_cond_y, phase_cond)
        if alt_cond and brg_cond and pos_cond_x and pos_cond_y and phase_cond:
            return True
        else:
            return False

    def get_phase(self, pos, brg, alt):
        list_check = [None, self.is_initial_climb, self.is_crosswind, self.is_downwind, self.is_base, self.is_final]
        phase_name = ['On the ground', 'Inital Climb', 'Crosswind', 'Downwind', 'Base', 'Final']

        for p in range(1, 6):
            check_fct = list_check[p]
            if check_fct(pos, brg, alt):
                if self.phase != p:
                    return p, phase_name[p]
                return None
        return None

    def tod(self, position, height, turn_dist):
        return False

    def get_message(self, position, height, turn_dist):
        if self.tod(position, height, turn_dist):
            return "Start the descent at -500 fpm"

        elif self.phase == 1 and height >= param.INITIAL_MIN_HEIGHT:
            return self.turn_side_msg + "Crosswind"

        elif self.phase == 2 and position[1] >= self.crosswind_dist - turn_dist:
            return self.turn_side_msg + "Downwind"

        elif self.phase == 3 and position[0] * -1 >= self.crosswind_dist - turn_dist:
            return self.turn_side_msg + "Base"

        elif self.phase == 4 and position[1] <= turn_dist:
            return self.turn_side_msg + "Final"

        else:
            return None


if __name__ == "__main__":

    sm = SimConnection()
    circuit = CurrentCircuit(param.DB_PATH, param.CIRCUIT)

    while 1:
        plane_pos = circuit.local_coord(sm.get_position())  # In circuit local coord system
        plane_brg = brg_limit(sm.get_hdg_true() - circuit.heading_true)  # In circuit local coord system
        plane_height = sm.get_true_alt() - circuit.airport_alt
        print(plane_pos, plane_brg, plane_height, sm.is_on_ground())

        if sm.is_on_ground():
            circuit.phase = 0
        else:
            new_phase = circuit.get_phase(plane_pos, plane_brg, plane_height)
            if new_phase:
                circuit.phase = new_phase[0]
                sm.show_msg("Entering " + new_phase[1])

            circuit_msg = circuit.get_message(plane_pos, plane_height, sm.turn_dist)
            if circuit_msg:
                sm.show_msg(circuit_msg)

        sleep(param.ITERATION_DELAY)
