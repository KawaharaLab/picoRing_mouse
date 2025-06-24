import util.helper_visa as helper_visa
import datetime

class VisaEquipment():  # Super Class for Visa Equipment

    def __init__(self, device_name):
        self.device_name = device_name
        self.rm = helper_visa.ResourceManager('@py')
        self.mi = self.rm.open_resource(device_name)

    def command(self, cmd):
        self.mi.write(cmd)

    def readas(self, cmd):
        self.mi.query_ascii_values(cmd)

    def read(self):
        return self.mi.read()

    def reset(self):
        self.command("*RST")

    def clear(self):
        self.command("*CLS")

    def display_off(self):
        self.command("DISP OFF")

    def display_on(self):
        self.command("DISP ON")

    def is_done(self):
        self.command("*OPC?")
        return int((self.mi.read()).strip())

    def close(self):
        self.rm.close()

    def __del__(self):
        self.rm.close()

class VnaZnb(VisaEquipment):

    def __init__(self, dev_name):
        super().__init__(dev_name)

    def __del__(self):
        super().__del__()

    def initial_process(self):
        super().reset()
        super().clear()

    def command(self, cmd):
        super().command(cmd)

    def set_trace(self, trace_name, sparam):
        super().command("CALC1:PAR:DEL:ALL")  # Deletes all traces before assigning.
        super().command("CALC1:PAR:SDEF {0}, {1}".format(trace_name, sparam))

    def display_trace(self, trace_name):
        super().command("DISP:WIND2:STAT ON")
        super().command("DISP:WIND2:TRAC:FEED {}".format(trace_name))

    def set_port(self, log_port, phys_port):
        super().command("SOUR:LPOR{0} {1}".format(log_port, phys_port))

    def set_calc_form(self, calc_form):
        super().command("CALC1:FORM {}".format(calc_form))

    def set_freq_range(self, start_freq, stop_freq):
        super().command("FREQ:STAR {}".format(start_freq))
        super().command("FREQ:STOP {}".format(stop_freq))

    def set_freq_bandwidth(self, freq):
        super().command("BAND {}".format(freq))

    def set_timedomain(self, filter, edge):
        super().command("CALC1:TRAN:TIME:STAT ON")  # Activating the frequency sweep, and enable the time domain transformation.
        super().command("CALC1:TRAN:TIME {}".format(filter))
        super().command("CALC1:TRAN:TIME:STIM {}".format(edge))
        super().command("HARM:AUTO ON")  # Turns the "Automatic Harmonic Grid" function ON

    def set_timedomain_range(self, start_time, stop_time):
        super().command("CALC1:TRAN:TIME:STAT ON")  # Activating a time gate.
        super().command("CALC1:TRAN:TIME:STAR {}".format(start_time))
        super().command("CALC1:TRAN:TIME:STOP {}".format(stop_time))

    def set_sweep_number(self, sweep_number):
        super().command("AVER ON")  # Enable the automatic calculation of the sweep average over the specified number of sweeps.
        super().command("AVER:COUN {}".format(sweep_number))

    def initiate_calibration(self, cal_type):
        super().command("SENS1:CORR:COLL:AUTO:TYPE {}".format(cal_type))

    def assign_calibration(self, test_port, cal_unit_port):
        super().command("SENS1:CORR:COLL:AUTO:ASS1:DEL:ALL")  # Deletes all available port assignments.
        super().command("SENS1:CORR:COLL:AUTO:ASS1:DEF {0}, {1}".format(test_port, cal_unit_port))

    def perform_calibration(self):
        super().command("SENS1:CORR:COLL:AUTO:ASS1:ACQ")
        super().command("SENS1:CORR:COLL:AUTO:SAVE")

    def create_file_name(self):
        current_time = datetime.datetime.now()
        current_time = "{0:%Y%m%d%H%M}".format(current_time)
        file_path = "C:\\Users\\Instrument\\Documents\\ikeda\\IkedaTdr" + str(current_time) + ".CSV"
        return file_path

    def create_photo_name(self):
        current_time = datetime.datetime.now()
        current_time = "{0:%Y%m%d%H%M}".format(current_time)
        file_path = "C:\\Users\\Instrument\\Documents\\ikeda\\IkedaTdr" + str(current_time) + ".BMP"
        return file_path

    def store_data(self, output_file, format_ind, format_type):
        super().command("MMEM:STOR:TRAC:CHAN 1, '{0}', {1}, {2}".format(output_file, format_ind, format_type))
        super().command("HCOP:DEST 'MMEM'")
        super().command("HCOP")

    def print_display(self, output_file):
        super().command("HCOP:DEV:LANG BMP")
        super().command("MMEM:NAME '{}'".format(output_file))
        super().command("HCOP:DEST 'MMEM'")
        super().command("HCOP")

    def move_data(self):
        super().command("MMEM:MOVE 'C:\\Users\\Instrument\\Documents\\ikeda\\piyo.csv', 'C:\\Users\\Instrument\\Documents\\ikeda\\fuga.csv'")

    def make_dir(self):
        super().command("MMEM:MDIR 'C:\\Users\\Instrument\\Documents\\ikeda\\new'")
