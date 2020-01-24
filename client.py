import os
from time import sleep
import threading
import tkinter as tk

from elkpy import sushicontroller as sc
SUSHI_ADDRESS = ('localhost:51051')
# Get protofile to generate grpc library
proto_file = os.environ.get('SUSHI_GRPC_ELKPY_PROTO')
if proto_file is None:
    print("Environment variable SUSHI_GRPC_ELKPY_PROTO not defined, set it to point the .proto definition")
    sys.exit(-1)


SLEEP_PERIOD = 0.0001# increase to limit the number of simultaneous set requests (Re's don't like that)
POLL_PERIOD = 1
COLUMN_HEIGHT = 15 # max widgets before starting a new column
SLIDER_WIDTH = 150
SLIDER_HEIGHT = 50

SYNCMODES = ["Internal", "Midi", "Gate", "Link"]

class PollingThread:
    def __init__(self, app):
        self.app = app
        self.running = True
        self.thread1 = threading.Thread(target=self.worker)
        self.thread1.start()

    def worker(self):
        while self.running:
            self.app.update()
            sleep(POLL_PERIOD)

    def stop(self):
        self.running = False


class App(tk.Frame):
    def __init__(self, controller, master=None):
        super().__init__(master)
        self.sushi = controller
        self.master = master
        self.widgets = []
        self.processor_params = {}
        self.pack(fill="both")
        self.create_widgets()

    def set_parameter(self, processor_id, parameter_id, value):
        self.sushi.set_parameter_value(processor_id, parameter_id, value) 
        sleep(SLEEP_PERIOD)
        ##txt_val = self.sushi.get_parameter_value_as_string(processor_id, parameter_id)
        ##self.value_display.delete(0, tk.END)
        ##self.value_display.insert(0, str(value) + " ("+str(txt_val.value)+")")

    def set_program(self, processor_id, program, programs):
        program_id = programs.index(program)
        self.sushi.set_processor_program(processor_id, program_id)
        sleep(SLEEP_PERIOD)
        self.refresh_param_values(processor_id)

    def set_sync_mode(self, str_mode):
        if str_mode == "Internal":
            mode = 1
        elif str_mode == "Midi":
            mode = 2
        elif str_mode == "Gate":
            mode = 2
        elif str_mode == "Link":
            mode = 3

        self.sushi.set_sync_mode(mode)

    def set_play_mode(self, mode):
        sushi_mode = 2 if mode else 1
        self.sushi.set_playing_mode(sushi_mode)

    def set_tempo(self, new_tempo):
        self.sushi.set_tempo(new_tempo)

    def stop(self):
        self.set_play_mode(False)
        self.stop_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.NORMAL)

    def play(self):
        self.set_play_mode(True)
        self.stop_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.DISABLED)


    def get_parameter(self, processor_id, parameter_id):
        try:
            return self.sushi.get_parameter_value(processor_id, parameter_id)
        except:
            return 0

    def refresh_param_values(self, processor_id):
        for i in self.processor_params[processor_id]:
            value = self.get_parameter(processor_id, i['id'])
            i['widget'].set(value)

    def create_widgets(self):
        self.create_transport_section()
        tracks = self.sushi.get_tracks()
        for t in tracks:
            self.create_track(t)
            separator = tk.Frame(self, height=2, width=2, bd=1, relief="sunken")
            separator.pack(fill="y", side="left", padx=5, pady=5)

    def create_track(self, track):
        processors = self.sushi.get_track_processors(track.id)
        frame = tk.Frame(self)
        frame.pack(fill="both", side="left")
        processor_count = 0

        for p in processors:
            if processor_count > 1:
                 new_frame = tk.Frame(self)
                 new_frame.pack(fill="both", side="left")
                 frame = new_frame
                 processor_count = 0

            processor_count += 1

            label = tk.Label(frame, text=p.label)
            label.pack(side="top")
            self.create_processor(frame, p)
            separator = tk.Frame(frame, self, height=2, width=2, bd=1, relief="sunken")
            separator.pack(fill="x", side="top", padx=5, pady=5)

        pan_vol_frame = tk.Frame(frame)
        params = self.sushi.get_track_parameters(track.id)
        for p in params:
            l = tk.Label(pan_vol_frame, text=p.name)
            l.pack(side="top")
            def_val = self.get_parameter(track.id, p.id)
            w = tk.Scale(pan_vol_frame, from_=p.min_range, to_=p.max_range, resolution=0.001, \
                 showvalue=False, orient=tk.HORIZONTAL,  length=SLIDER_WIDTH, \
                 command=lambda v,p=track.id,a=p.id: self.set_parameter(p, a, float(v)))
            w.pack(side="top")
            w.set(def_val)
            sleep(SLEEP_PERIOD)

        pan_vol_frame.pack(fill="y", side="bottom")

    def create_processor(self, parent, proc):
        params = self.sushi.get_processor_parameters(proc.id)
        proc_frame = tk.Frame(parent) 
        proc_frame.pack(fill="both", side="top")
        frame = tk.Frame(proc_frame, width=SLIDER_WIDTH) 
        frame.pack(fill="y", side="left")
        self.processor_params[proc.id] = []
        count = 0
        
        for p in params:
            if count > COLUMN_HEIGHT:
                new_frame = tk.Frame(proc_frame) 
                new_frame.pack(fill="y", side="left")
                count = 0
                frame = new_frame

            l = tk.Label(frame, text=p.name)
            l.pack(side="top")
            def_val = self.get_parameter(proc.id, p.id)
            w = tk.Scale(frame, from_=p.min_range, to_=p.max_range, resolution=0.001, \
                showvalue=False, orient=tk.HORIZONTAL, length=SLIDER_WIDTH, \
                command=lambda v,p=proc.id,a=p.id: self.set_parameter(p, a, float(v)))
            w.pack(side="top", fill="none")
            w.set(def_val)
            self.processor_params[proc.id].append({'id':p.id, 'widget':w})
            sleep(SLEEP_PERIOD)
            count += 1

        self.create_program_selector(frame, proc)
        self.create_bypass_button(frame, proc)
        #self.processor_params[proc.id] = []
    
    def create_program_selector(self, parent, proc):
        try:
            programs = self.sushi.get_processor_programs(proc.id)
            program_names = [p.name for p in programs]
            label = tk.Label(parent, text="Programs")
            label.pack(side="top")
            variable = tk.StringVar(parent)
            variable.set(program_names[0])
            selector = tk.OptionMenu(parent, variable, *program_names)
            selector.config(width=2)
            variable.trace('w', lambda v,a,b,p=proc.id,n=program_names,var=variable: self.set_program(p, var.get(), n))
            selector.pack(side="top", fill="both", expand=0)

        except:
            pass

    def create_bypass_button(self, frame, proc):
        var = tk.IntVar()
        button = tk.Checkbutton(frame, text = "Enabled", variable = var,
                 command=lambda v=var,p=proc.id: self.sushi.set_processor_bypass_state(p, not bool(v.get())))
        button.pack(side="top", fill="both", expand=0)

    def create_transport_section(self):
        frame = tk.Frame(self) 
        frame.pack(fill="y", side="top")

        variable = tk.StringVar(frame)
        variable.set(SYNCMODES[0])
        selector = tk.OptionMenu(frame, variable, *SYNCMODES)
        selector.config(width=6)
        variable.trace('w', lambda v,a,b,n=SYNCMODES,var=variable: self.set_sync_mode(var.get()))
        selector.pack(side="left", fill="both", expand=50)

        self.stop_button = tk.Button(frame, text="Stop", command=self.stop)
        self.stop_button.pack(fill="none", side="left")
        self.play_button = tk.Button(frame, text="Play", command=self.play)
        self.play_button.pack(fill="none", side="left")

        label = tk.Label(frame, text="Tempo")
        label.pack(side="left")
        #self.tempo_var = tk.StringVar(frame)
        #self.tempo_var.set("99")
        tempo_entry = tk.Spinbox(frame, from_=20, to=900, width=7)
        tempo_entry.config(command=lambda t=tempo_entry: self.set_tempo(float(t.get())))
        #self.tempo_var.trace('w', lambda var=self.tempo_var: self.set_tempo(var.get()))
        tempo_entry.pack(side="left")
        self.tempo_entry = tempo_entry

    def update(self):
        tempo = self.sushi.get_tempo()
        if str(int(tempo)) != self.tempo_entry.get():
            self.tempo_entry.delete(0, tk.END)
            self.tempo_entry.insert(0, str(int(tempo)))

def main():
    controller = sc.SushiController(SUSHI_ADDRESS, proto_file)
    root = tk.Tk()
    root.wm_title("Sushi")
    app = App(controller, master=root)
    poll = PollingThread(app)
    app.mainloop()
    poll.stop()

if __name__ == "__main__": main()
