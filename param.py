# DB_PATH = r"C:\Users\Florian\AppData\Roaming\ABarthel\little_navmap_db\little_navmap_navigraph.sqlite"
DB_PATH = r"C:\Users\Florian\AppData\Roaming\ABarthel\little_navmap_db\little_navmap_msfs.sqlite"

CIRCUIT = {'airport': "LFBR",
           'rwy': "29",
           'side': "LHS"}

AIRCRAFT = {'name': 'C172',
            'Vrotate': 55,
            'Vinit_climb': 75,
            'Vcruise': 105,
            'Vapp': 75,
            'Vland': 65,
            'Max_climb_speed': 80,
            'Min_VS': 350,
            'Normal_VS': 500,
            'Vstall': 40}

DISPLAY_MSG = {'enter_init_climb': False,
               'enter_crosswind': False,
               'enter_downwind': True,
               'enter_base': False,
               'enter_final': False,
               'enter_ground': False}

IVAO_SEND_MSG = {'enter_init_climb': True,
                 'enter_crosswind': False,
                 'enter_downwind': True,
                 'enter_base': False,
                 'enter_final': True,
                 'enter_ground': False}

MSG_KEYS = ['enter_ground', 'enter_init_climb', 'enter_crosswind', 'enter_downwind', 'enter_base', 'enter_final']

INITIAL_MIN_HEIGHT = 500  # ft AAL
INIT_CLIMB_TIME = 60  # s
CROSSWIND_TIME = 60  # s
BASE_START = 45  # °
BANK_ANGLE_SAFE = 20  # °
BANK_ANGLE = 30  # °
TOL_DIS = 0.4  # NM
TOL_ANG = 45  # °
TOL_ALT = 300  # ft
FLAPS_UP_ALT = 300  # ft

METER2FEET = 3.28084
NM2METER = 1852
NM2FEET = NM2METER * METER2FEET
G = 9.81  # m/s²

EARTH_RADIUS = 6378137  # meters

# Sleep time between each iteration
ITERATION_DELAY = 1  # s
T_LAG = 10  # s
