import requests
import time
import threading
from ioexpand import PCF8574
from vfdcontrol import Debouncer

SEEBURG_QUARTER = 4
SEEBURG_DIME = 1
SEEBURG_NICKLE = 2

SEEBURG_BUTTON1 = 32
SEEBURG_BUTTON2 = 64
SEEBURG_SIGNAL = 128

class Seeburg(PCF8574):
    def __init__(self, bus, addr):
        PCF8574.__init__(self, bus, addr)
        self.set_gpio(0, SEEBURG_QUARTER | SEEBURG_DIME | SEEBURG_NICKLE | SEEBURG_BUTTON1 | SEEBURG_BUTTON2 | SEEBURG_SIGNAL)

    def insert_quarter(self):
        self.not_gpio(0, SEEBURG_QUARTER)
        time.sleep(0.25)
        self.or_gpio(0, SEEBURG_QUARTER)

    def insert_dime(self):
        self.not_gpio(0, SEEBURG_DIME)
        time.sleep(0.25)
        self.or_gpio(0, SEEBURG_DIME)

    def insert_nickle(self):
        self.not_gpio(0, SEEBURG_NICKLE)
        time.sleep(0.25)
        self.or_gpio(0, SEEBURG_NICKLE)

    def read_signal(self):
        if (self.get_gpio(0) & SEEBURG_SIGNAL) != 0:
            return 0
        else:
            return 1

    def read_button1(self):
        return ((self.get_gpio(0) & SEEBURG_BUTTON1) != 0)

    def read_button2(self):
        return ((self.get_gpio(0) & SEEBURG_BUTTON2) != 0)


class SeeburgThread(threading.Thread):
    def __init__(self, bus, addr, vfd=None, stereo_url=None, song_table={}):
        super(SeeburgThread, self).__init__()
        self.seeburg = Seeburg(bus, addr)

        self.quarter_signal = False
        self.dime_signal = False
        self.nickel_signal = False

        self.daemon = True

        self.pre_gap_count = 0
        self.post_gap_count = 0
        self.after_gap = False

        self.vfd = vfd
        self.last_vfd_1 = True
        self.last_vfd_2 = True
        self.last_vfd_3 = True

        if vfd:
            self.vfd_debouncer = Debouncer()

        self.debouncer = Debouncer()

        self.stereo_url = stereo_url
        self.song_table = song_table

    def insert_quarter(self):
        self.quarter_signal = True

    def insert_dime(self):
        self.dime_signal = True

    def insert_nickel(self):
        self.nickel_signal = True

    def run(self):
        last_state = 0
        last_tick_time = time.time()

        while True:
            if self.vfd:
                self.poll_vfd()

            self.poll_buttons()

            if (self.quarter_signal):
                self.seeburg.insert_quarter()
                self.quarter_signal = False

            if (self.dime_signal):
                self.seeburg.insert_dime()
                self.dime_signal = False

            if (self.nickel_signal):
                self.seeburg.insert_nickle()
                self.nickel_signal = False

            state = self.seeburg.read_signal()
            if (state != last_state):
                tick_time = time.time()

                if state == 0:
                    # 1->0 transition
                    self.handle_tick(tick_time - last_tick_time)

                last_state = state
                last_tick_time = tick_time

            if (time.time()-last_tick_time > 1):
                self.handle_endsignal()

            time.sleep(0) # .01)

    def handle_tick(self, elapsed):
        print elapsed
        if (elapsed < 0.07):
            print "tick"
            if (self.after_gap):
                self.post_gap_count += 1
            else:
                self.pre_gap_count += 1

        elif (elapsed < 0.35):
          print "gap"
          self.after_gap = True
          self.post_gap_count = 1

    def handle_endsignal(self):
        if (self.after_gap):
            self.handle_result(self.pre_gap_count, self.post_gap_count)
        self.pre_gap_count = 0
        self.post_gap_count = 0
        self.after_gap = False

    def number_to_letter(self,x):
        lettermap = {1: "A",
                     2: "B",
                     3: "C",
                     4: "D",
                     5: "E",
                     6: "F",
                     7: "G",
                     8: "H",
                     9: "J",
                    10: "K",
                    11: "L",
                    12: "M",
                    13: "N",
                    14: "P",
                    15: "Q",
                    16: "R",
                    17: "S",
                    18: "T",
                    19: "U",
                    20: "V"}

        if x in lettermap:
            return lettermap[x]
        else:
            return "%s" % x

    def handle_result(self, pre_gap_count, post_gap_count):
        print "result:", pre_gap_count, post_gap_count

        if self.vfd:
            self.vfd.setPosition(0,0)
            self.vfd.writeStr("Select: %s-%d " % (self.number_to_letter(pre_gap_count), post_gap_count))

        if self.stereo_url:
            select_code = "%s%d" % (self.number_to_letter(pre_gap_count), post_gap_count)
            song_dict = self.song_table.get(select_code)
            if song_dict:
                song_filename = song_dict["filename"]
                r = requests.get(self.stereo_url+"/queueFile?value=%s&artist=%s&song=%s" % \
                                 (song_dict["filename"].replace(" ","%20"),
                                  song_dict["artist"].replace(" ","%20"),
                                  song_dict["song"].replace(" ","%20")))
                print "stereo url result:", r.status_code
            else:
                print "failed to resolve song select code for %s" % select_code

    def skip_song(self):
        if self.stereo_url:
            r = requests.get(self.stereo_url + "/nextSong")
            print "stereo nextsong url result:", r.status_code

    def poll_buttons(self):
        (button1_db, button2_db) = self.debouncer.debounce_list([self.seeburg.read_button1(),
                                                                 self.seeburg.read_button2()])
        if (button1_db):
            self.quarter_signal = True

        if (button2_db):
            self.skip_song()

    def poll_vfd(self):
        self.vfd.poll_input()
        [button1_db, button2_db, button3_db, button_enc_db] = \
            self.vfd_debouncer.debounce_list([self.vfd.button1_state, self.vfd.button2_state,
                                              self.vfd.button3_state, self.vfd.button_enc_state])

        if button1_db:
            self.quarter_signal = True

        if button2_db:
            self.dime_signal = True

        if button3_db:
            self.nickel_signal = True

        if button_enc_db:
            self.skip_song()
        """
        if (self.last_vfd_1 != self.vfd.button1_state):
            self.last_vfd_1 = self.vfd.button1_state
            if self.vfd.button1_state:
                self.quarter_signal = True
        if (self.last_vfd_2 != self.vfd.button2_state):
            self.last_vfd_2 = self.vfd.button2_state
            if self.vfd.button2_state:
                self.dime_signal = True
        if (self.last_vfd_3 != self.vfd.button3_state):
            self.last_vfd_3 = self.vfd.button3_state
            if self.vfd.button3_state:
                self.nickel_signal = True
        """
