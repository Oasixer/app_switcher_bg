from enum import Enum
import datetime
import re

TERMITE_MATCH_REGEX = re.compile('(^nvim)|(sudo -E nvim)|(sudo nvim)|(/usr/bin/nvim)')

def is_nvim(window_title):
    return TERMITE_MATCH_REGEX.match(window_title) is not None

def get_program_name(window_title, class_name):
    #  print(f'{class_name}')
    for pn in ProgramName:
        if pn.value == class_name:
            print(f'matched {pn.value}')
            if pn is ProgramName.TERMITE:
                print(f'checking is_nvim for {window_title}: {is_nvim(window_title)}')
                if is_nvim(window_title):
                    return ProgramName.NVIM.value
            return pn.value
    return class_name.split('.')[0].lower()



class ProgramName(Enum):
    NVIM = 'nvim'
    TERMITE = 'termite.Termite'
    CHROME = 'google-chrome.Google-chrome'

class Program:
    def __init__(self, name, windows=[]):
        self.windows = windows
        #  print(f'WINDOWS????? {self.windows}')
        self.name = name

    def add(self, window):
        self.windows.append(window)
    
    def remove(self, window):
        self.windows.remove(window)

    def get(self, id: str):
        for w in self.windows:
            if w.id == id:
                return w

    def update(self, id: str, geometry: tuple, monitor: int, tag:str=None):
        w = self.get(id=id)
        w.update(geometry=geometry, monitor=monitor, tag=tag)

    @property
    def last_active(self):
        last = datetime.datetime(1000, 1, 1)
        for w in self.windows:
            if w.last_active > last:
                last = w.last
        return last
    
    def last_active_win(self, restrict_visits):
        last = datetime.datetime(1000, 1, 1)
        win = None
        for w in self.windows:
            if w.last_active > last:
                if not (restrict_visits and w.visited_during_request_series):
                    last = w.last_active
                    win = w
        return win
    
    def second_last_active_win(self, restrict_visits):
        if len(self.windows) == 1:
            return self.windows[0]
        last = datetime.datetime(1000,1,1)
        wins = [w for w in self.windows if not (restrict_visits and w.visited_during_request_series)]
        wins.sort(key=lambda w: w.last_active)
        return wins[-2]
# TODO add autoincrementing window IDs for each type so you can go straight to the memorized ID
# allow assigning arbitrary words to a window to find it fast!!!!!! or exclude it!!!!!
# ie. name a window "doc" then you find open documentation fast
# or name a window 
class Window:
    def __init__(self, id: str, program: Program, window_title: str, geometry: tuple, monitor: int, tag:str=None):
        self.id = id
        self.program = program
        self.geometry = geometry
        self.tag = tag
        self.monitor = monitor
        self.last_active = datetime.datetime.now()
        self.visited_during_request_series = False
        self.window_title = window_title
        self.updated = True

    def update(self, geometry: tuple, monitor: int, window_title:str, tag:str=None):
        self.geometry = geometry
        self.tag = tag
        self.monitor = monitor
        self.updated = True
        self.window_title = window_title

    def active(self):
        self.last_active = datetime.datetime.now()

    def __str__(self):
        return f'id: {self.id}, window_title: {self.window_title}, program: {self.program.name}, tag: {self.tag}'


class Root:
    def __init__(self, windows=[], programs=[]):
        self.windows = windows
        self.programs = programs

    def get(self, id: str) -> Window:
        for w in self.windows:
            if w.id == id:
                return w

        return None

    def get_active(self):
        if not self.windows:
            return None
        active = self.windows[0]
        for w in self.windows:
            if w.last_active > active.last_active:
                active = w

        return active

    def get_program_by_name(self, name):
        for p in self.programs:
            if p.name == name:
                return p
        return None

    def has_id(self, id: str) -> bool:
        for w in self.windows:
            if w.id == id:
                return True
        return False

    def update_active(self, id: str) -> None:
        #  print(f'id: {id}_')
        w = self.get(id=id)
        #  print([i.id for i in self.windows])
        w.active()

    def set_all_updated_false(self):
        for w in self.windows:
            w.updated = False
    
    def delete_non_updated(self):
        for w in self.windows:
            if not w.updated:
                if len(w.program.windows) == 1:
                    self.programs.remove(w.program)
                self.windows.remove(w)

    def add_or_update_windows(self, windows):
        for w in windows:
            id = w['id']
            monitor = w['monitor']
            geometry = (w['width'], w['height'])
            class_name = w['class_name']
            window_title = w['window_title']
            self.add_or_update_window_from_wmctrl(id=id,
                                                  monitor=monitor,
                                                  geometry=geometry,
                                                  class_name=class_name,
                                                  window_title=window_title)
        #  print(f'windows before delete: {self.windows}')
        #  for w in self.windows:
            #  print(w.updated)
        #  sp = self.get_program_by_name('spotify')
        #  print(f'LOOKING 4 SPOTIFY b4 STUFF: {sp.windows}')

        self.delete_non_updated()

        self.set_all_updated_false()
        #  print(f'LOOKING 4 SPOTIFY after STUFF: {sp.windows}')

    def add_or_update_window_from_wmctrl(self, id: str, monitor: int, geometry: tuple, class_name: str, window_title: str):
        # get the input for this by parsing a wmctrl -xGl call
        program_name = get_program_name(window_title=window_title, class_name=class_name).lower()
        program = None
        for p in self.programs:
            if p.name == program_name:
                program = p

        if program is None:
            program = Program(name=program_name, windows=[])
            self.programs.append(program)
            #  print(f'HIS FUCKING WINDOWS ARE NOW: {program.windows}')

        w = self.get(id=id)
        if w is None:
            w = Window(id=id, program=program, window_title=window_title, geometry=geometry, monitor=monitor)
            w.program = program
            program.add(w)
            self.windows.append(w)
            #  if program_name == 'spotify':
                #  print(f'appending window: {w} to program: {program.name}')
                #  print(f'MY FUCKING WINDOWS ARE NOW: {program.windows}')
        else:
            w.update(geometry=geometry, monitor=monitor, window_title=window_title)

    def get_window_matching_tag(self, input_chars, active_window, active_program, restrict_visits):
        matching = []
        for w in self.windows:
            if w is not active_window:
                if w.tag is not None:
                    if w.tag.startswith(input_chars):
                        matching.append(w)

        if not matching:
            return None

        if len(matching) == 1:
            return matching[0]

        most_recent = matching[0]
        for w in matching:
            if w.last_active > most_recent.last_active:
                most_recent = w
        
        return most_recent
    
    def get_window_matching_program(self, input_chars, active_window, active_program, restrict_visits):
        matching_programs = []
        for p in self.programs:
            print(p.name)
            if p.name.startswith(input_chars):
                #  print(f'MATCHING PNAME: {p.name} | {p.name.startswith(input_chars)}')
                matching_programs.append(p)
        if not matching_programs:
            return None
        if len(matching_programs) == 1:
            #  print("ONE MATCHING")
            program = matching_programs[0]
            if active_window.program is program:
                #  print("ACTIVE WINDOW IS PROGRAM")
                return program.second_last_active_win(restrict_visits)
            else:
                #  print(f"SPOTIFY INDEX: {self.programs.index(program)}")
                #  print(f"SPOTIFY WINDOWS:")
                #  print(f"RETURNING PROGRAM LAST ACTIVE WIN FOR {program.name}: {program.last_active_win(restrict_visits)}")
                return program.last_active_win(restrict_visits)
        matching = []
        for w in self.windows:
            if w is not active_window:
                if w.program is not active_program:
                    if w.program.name.startswith(input_chars):
                        if not (restrict_visits and w.visited_during_request_series):
                            matching.append(w)

        if len(matching) == 1:
            return matching[0]

        most_recent = matching[0]
        for w in matching:
            if w.last_active > most_recent.last_active:
                most_recent = w
        
        return most_recent


    def get_matching(self, input_chars: str):
        active_window = self.get_active()
        if active_window is None:
            return None
        active_program = active_window.program

        restrict_visits = False

        for i in range(2):
            print(f"finding matching. restrict_visits={restrict_visits}")
            w = self.get_window_matching_tag(input_chars, active_window, active_program, restrict_visits)

            if w is None:
                w = self.get_window_matching_program(input_chars, active_window, active_program, restrict_visits)
                if w is not None:
                    print(f'found window by program name: {w}')
            else:
                print(f'found window by tag: {w}')

            if w is not None:
                w.visited_during_request_series = True
                w.last_active = datetime.datetime.now()
                break
            else:
                restrict_visits = True

        if w is not None:
            print(f'found window: {w} for input_chars: {input_chars}')
        return w

    def flush_visited(self):
        for w in self.windows:
            w.visited_during_request_series = False


# examples:
# windows:
# slack, spotify

# input_chars:
# s
# if slack is already active, switch to the most recent spotify window and vice versa.
# sl
