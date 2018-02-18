import time
import threading
from ioexpand import PCF8574

SEEBURG_QUARTER = 4
SEEBURG_DIME = 1
SEEBURG_NICKLE = 2

SEEBURG_SIGNAL = 128

class Seeburg(PCF8574):
    def __init__(self, bus, addr):
        PCF8574.__init__(self, bus, addr)
        self.set_gpio(0, SEEBURG_QUARTER | SEEBURG_DIME | SEEBURG_NICKLE | SEEBURG_SIGNAL)

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

class SeeburgThread(threading.Thread):
    def __init__(self, bus, addr):
        super(SeeburgThread, self).__init__()
        self.seeburg = Seeburg(bus, addr)

        self.quarter_signal = False
        self.dime_signal = False
        self.nickel_signal = False

        self.daemon = True

        self.pre_gap_count = 0
        self.post_gap_count = 0
        self.after_gap = False

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
                self.show_result()

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

    def show_result(self):
        if (self.after_gap):
            print "result: ", self.pre_gap_count, self.post_gap_count
        self.pre_gap_count = 0
        self.post_gap_count = 0
        self.after_gap = False