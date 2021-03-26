from enum import Enum
import re

TERMITE_MATCH_REGEX = re.compile('(^nvim)|(sudo -E nvim)|(sudo nvim)')

def is_nvim(window_title):
    return TERMITE_MATCH_REGEX.match(window_title) is not None

class ProgramName(Enum):
    NVIM = 'nvim'
    TERMITE = 'termite.Termite'
    CHROME = 'google-chrome.Google-chrome'

class Program:
    def __init__(self, name):
        self.windows = []

    def add(self, window):
        self.windows.append(window)
    
    def remove(self, window):
        self.windows.remove(window)

def get_program_name(window_title, class_name):
    for pn in ProgramName:
        if pn.value == class_name:
            if pn is ProgramName.TERMITE:
                if is_nvim(window_title):
                    return ProgramName.NVIM
            return pn

    raise Exception

# TODO add autoincrementing window IDs for each type so you can go straight to the memorized ID
# allow assigning arbitrary words to a window to find it fast!!!!!! or exclude it!!!!!
# ie. name a window "doc" then you find open documentation fast
# or name a window 
class Window:
    def __init__(self, id: str, program: Program, geometry: tuple, monitor: int, tag=None: str):
        self.id = id
        self.program = program
        self.geometry = geometry
        self.tag = tag
        self.monitor = monitor


class Root:
    def __init__(self, windows, programs):
        self.windows = windows
        self.programs = programs
    
    @staticmethod # todo double check syntax
    def add_window_from_wmctrl(self, id: str, monitor: int, geometry: tuple, class_name: str, window_title: str):
        # get the input for this by parsing a wmctrl -xGl call
        program_name = get_program_name(window_title=window_title, class_name=class_name)
        program = None
        for p in self.programs:
            if p.name is program_name:
                program = p
        if program is None:
            program = Program() # todo args

        window = Window(id=id, program=program, geometry=geometry, monitor=monitor)

        window.program = program
        program.add()


