import param
from time import sleep
from RunwayData import LocalCircuit
from CoordCalc import brg_limit, resultante
from SimConnectInterface import SimConnection
from math import pi, asin, degrees, radians, sin
from IVAO_interface import Window


class CurrentCircuit(LocalCircuit):
    def __init__(self, db_path, circuit_input_data, sim_connection):
        self.sm = sim_connection
        LocalCircuit.__init__(self, db_path, circuit_input_data, sm.get_position())

        self.ivao_window = Window("IVAO Pilot Client")
        self.msfs_window = Window("Microsoft Flight Simulator")

        self.phase = 10
        self.phase_name = "Outside airport circuit"
        self.msg_displayed = {'start_descent': False,
                              'take_off': False,
                              'turn_crosswind': False,
                              'turn_downwind': False,
                              'turn_base': False,
                              'turn_final': False,
                              'flaps_up': False,
                              'reduce_speed': False,
                              'maintain_alt': False,
                              'light_on': False,
                              'light_off': False}

        if self.side == "LHS":
            self.turn_side_msg = "Turn left in "
            self.side_msg = "left hand"
        else:
            self.turn_side_msg = "Turn right in "
            self.side_msg = "right hand"

        self.descent_angle = degrees(asin(param.AIRCRAFT['Normal_VS'] /
                                          (param.AIRCRAFT['Vapp'] * param.NM2FEET / 60)))

        self.crosswind_dist = None
        self.max_crosswind_x = None
        self.get_crosswind_data()

    def get_crosswind_data(self):
        self.crosswind_dist = param.AIRCRAFT['Vinit_climb'] / 3600 * param.CROSSWIND_TIME
        self.max_crosswind_x = 500 / param.AIRCRAFT['Min_VS'] * param.AIRCRAFT['Max_climb_speed'] / 60 + self.length
        # time to climb to 500ft at min VS and max climb speed, + runway length

    def dist2land(self, pos, turn_radius):
        delta_turn = turn_radius * (2 - pi / 2)
        if self.phase == 3:
            return self.d_target + self.crosswind_dist - delta_turn, self.crosswind_dist * 2 + pos[0] - delta_turn
        elif self.phase == 4:
            return self.d_target + self.crosswind_dist - delta_turn, pos[1]
        elif self.phase == 5:
            return self.d_target - pos[0], 0
        else:
            return self.d_target + self.crosswind_dist - delta_turn, 999999

    def is_on_ground(self, pos, brg, alt):
        cond_pos_x = 0 < pos[0] * param.NM2FEET < self.length
        cond_pos_y = -100 < pos[1] * param.NM2FEET < 100
        cond_brg = brg < param.TOL_ANG or brg >= 360 - param.TOL_ANG  # heading 360?? more or less 45??
        cond_alt = alt < 20
        cond_phase = not self.is_initial_climb(pos, brg, alt) and not self.is_final(pos, brg, alt)
        if cond_pos_x and cond_pos_y and cond_brg and cond_alt and cond_phase:
            return True
        else:
            return False

    def is_initial_climb(self, pos, brg, alt):
        alt_cond = 20 < alt < self.pattern_altitude + param.TOL_ALT  # above 50ft AAL and below patern alt + tolerance
        brg_cond = brg < param.TOL_ANG or brg >= 360 - param.TOL_ANG  # heading 360?? more or less 45??
        pos_cond_x = pos[0] > 0  # In front of the runway
        pos_cond_y = 0 - param.TOL_DIS < pos[1] < 0 + param.TOL_DIS  # in the axis of the runway more or less tolerance
        vs_cond = sm.get_vs() > 300
        if alt_cond and brg_cond and pos_cond_x and pos_cond_y and vs_cond:
            return True
        else:
            return False

    def is_crosswind(self, pos, brg, alt):
        alt_cond = self.pattern_altitude / 2 - param.TOL_ALT < alt < self.pattern_altitude + param.TOL_ALT
        brg_cond = 270 - param.TOL_ANG <= brg < 270 + param.TOL_ANG  # heading 270?? more or less 45??
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
        alt_cond = 20 <= alt < self.pattern_altitude + param.TOL_ALT
        brg_cond = brg < param.TOL_ANG or brg >= 360 - param.TOL_ANG  # heading 360?? more or less 45??
        pos_cond_x = -1.6 - param.TOL_DIS < pos[0] < self.length / 2
        pos_cond_y = 0 - param.TOL_DIS < pos[1] < 0 + param.TOL_DIS  # in the axis of the runway more or less tolerance
        phase_cond = 2 < self.phase <= 5
        if alt_cond and brg_cond and pos_cond_x and pos_cond_y and phase_cond:
            return True
        else:
            return False

    def reinit_msg(self):
        print('msg_displayed reinit')
        for k in self.msg_displayed:
            self.msg_displayed[k] = False

    def update_phase(self, pos, brg, alt):
        list_check = [self.is_on_ground, self.is_initial_climb, self.is_crosswind, self.is_downwind, self.is_base,
                      self.is_final]
        name = ['On the ground', 'Inital Climb', 'Crosswind', 'Downwind', 'Base', 'Final']

        current_phase = 10
        for p in range(0, 6):
            check_fct = list_check[p]
            if check_fct(pos, brg, alt):
                current_phase = p
                if self.phase != current_phase and \
                        ((self.phase == 10 and current_phase in (0, 3, 5)) or self.phase < 10):
                    self.phase_name = name[current_phase]
                    self.phase = current_phase
                    self.situation_msg()
                    if p == 0:
                        self.get_crosswind_data()
                        self.reinit_msg()
                    break

        if current_phase == 10:
            self.phase = 10
            self.phase_name = "Outside airport circuit"

    def get_message(self, position, height, turn_dist, is_ground, ias):

        dist = self.dist2land(position, turn_dist)
        potential_h = dist[0] * sin(radians(self.papi_angle)) + dist[1] * sin(radians(self.descent_angle))
        potential_h *= param.NM2FEET

        if potential_h <= height and self.phase >= 3 and not self.msg_displayed['start_descent']:
            self.msg_displayed['start_descent'] = True
            self.sm.show_msg("Start descent at " + str(param.AIRCRAFT['Vapp']) + "kt and -" +
                             str(round(param.AIRCRAFT['Normal_VS'], 0)) + "fpm")

        elif self.phase == 0 and is_ground and ias >= param.AIRCRAFT['Vrotate'] and not self.msg_displayed['take_off']:
            self.msg_displayed['take_off'] = True
            self.sm.show_msg("VR, takeoff")

        elif self.phase == 1 and height >= param.FLAPS_UP_ALT and not self.msg_displayed['flaps_up']:
            self.msg_displayed['flaps_up'] = True
            self.sm.show_msg("Flaps up")

        elif self.phase == 1 and height >= param.INITIAL_MIN_HEIGHT and not self.msg_displayed['turn_crosswind']:
            self.msg_displayed['turn_crosswind'] = True
            self.sm.show_msg(self.turn_side_msg + "Crosswind")

        elif self.phase == 2 and position[1] >= self.crosswind_dist - turn_dist and \
                not self.msg_displayed['turn_downwind']:
            self.msg_displayed['turn_downwind'] = True
            self.sm.show_msg(self.turn_side_msg + "Downwind")

        elif 1 <= self.phase <= 3 and height >= self.pattern_altitude - 100 and \
                not self.msg_displayed['maintain_alt']:
            self.msg_displayed['maintain_alt'] = True
            maintain_alt = round((self.pattern_altitude + self.airport_alt) / 100, 0) * 100
            self.sm.show_msg("Maintain runway circuit altitude " + str(maintain_alt) + "ft")

        elif self.phase == 3 and position[0] <= 0 and not self.msg_displayed['reduce_speed']:
            self.msg_displayed['reduce_speed'] = True
            self.sm.show_msg("Reduce speed to " + str(param.AIRCRAFT['Vapp']) + "kt and set Flaps 10??")

        elif self.phase == 3 and position[0] * -1 >= self.crosswind_dist - turn_dist and \
                not self.msg_displayed['turn_base']:
            self.msg_displayed['turn_base'] = True
            self.sm.show_msg(self.turn_side_msg + "Base")

        elif self.phase == 4 and position[1] <= turn_dist and not self.msg_displayed['turn_final']:
            self.msg_displayed['turn_final'] = True
            self.sm.show_msg(self.turn_side_msg + "Final, reduce speed to " + str(param.AIRCRAFT['Vland']) +
                             "kt and set full Flap")

        elif self.phase == 10 and not self.msg_displayed['light_off'] and \
                (self.airport_ident != param.CIRCUIT['start_airport'] or resultante(position) > param.LIGHT_OFF_DIST):
            self.sm.show_msg("Landing Light OFF")
            self.msg_displayed['light_off'] = True

        elif self.phase == 10 and self.airport_ident == param.CIRCUIT['airport'] and \
                resultante(position) < param.LIGHT_ON_DIST and not self.msg_displayed['light_on']:
            self.sm.show_msg("Landing Light ON")
            self.msg_displayed['light_on'] = True

        # print(self.phase == 10, self.airport_ident == param.CIRCUIT['airport'], resultante(position) < 1,
        #       not self.msg_displayed['light_on'])
        # print(resultante(position))

    def situation_msg(self):
        if 0 < self.phase < 10:
            msg = self.airport_ident + " traffic, " + param.AIRCRAFT['name']
            if self.phase == 1:
                msg += " Airborne off"
            elif self.phase == 5:
                msg += " on Final"
            elif 2 <= self.phase <= 4:
                msg += " join " + self.side_msg + " " + self.phase_name

            msg += " Runway " + param.CIRCUIT['rwy']

            if param.DISPLAY_MSG[param.MSG_KEYS[self.phase]]:
                self.sm.show_msg(msg)
            if param.IVAO_SEND_MSG[param.MSG_KEYS[self.phase]] and self.sm.is_ivao_unicom() and self.ivao_window.hwnd:
                self.ivao_window.send_txt(30, 350, msg)
                self.msfs_window.show()


if __name__ == "__main__":

    sm = SimConnection()
    circuit = CurrentCircuit(param.DB_PATH, param.CIRCUIT, sm)
    airport_timer = 0

    while 1:
        sm_position = sm.get_position()
        if sm_position and not sm.get_ias() is None:

            # If outside airport circuit, the closest airport is updated each 30s
            if circuit.phase == 10:
                airport_timer += 1
                if airport_timer >= 30 / param.ITERATION_DELAY:
                    airport_timer = 0
                    circuit.get_closest_airport(sm_position)

            plane_pos = circuit.local_coord(sm_position)  # In circuit local coord system
            plane_brg = brg_limit(sm.get_hdg_true() - circuit.heading_true)  # In circuit local coord system
            if circuit.side == "RHS":
                plane_brg = brg_limit(360 - plane_brg)
            plane_height = sm.get_true_alt() - circuit.airport_alt
            turn_d = sm.turn_dist()

            circuit.update_phase(plane_pos, plane_brg, plane_height)
            circuit.get_message(plane_pos, plane_height, turn_d, sm.is_on_ground(), sm.get_ias())

            # Print in terminal the main flight parameters
            print(circuit.airport_ident, circuit.rwy_ident, circuit.phase, circuit.phase_name, round(plane_pos[0], 2),
                  round(plane_pos[1], 2), round(plane_brg, 0), round(plane_height, 0))

        sleep(param.ITERATION_DELAY)
