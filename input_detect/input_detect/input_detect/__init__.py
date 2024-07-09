import pyaudio
import threading
from array import array
import warnings

class ThresholdDetect(object):
    def __init__(self):
        self.frames = []
        self.in_recording = False
        self.means = []
        self.mean = None

    def init(
        self,
        chunk=1024,
        sample_format=pyaudio.paInt16,
        channels=1,
        fs=44100,
        duration=None,
        force_init=False,
    ):
        if self.in_recording:
            if force_init:
                warnings.warn("Previous recording forced to terminate.")
                self.terminate_recording()
            else:
                raise Exception("EMG in recording. Teminate the recording first.")

        self.chunk = chunk
        self.sample_format = sample_format
        self.channels = channels
        self.fs = fs
        self.duration = duration

        self.continue_recording = True

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            format=self.sample_format,
            channels=self.channels,
            rate=self.fs,
            frames_per_buffer=self.chunk,
            input=True,
        )

    def start_recording(self):
        def to_do():
            self.in_recording = True
            self.recording_loop_terminated = False
            if self.duration != None:
                for _ in range(0, int(self.fs / self.chunk * self.duration)):
                    if self.continue_recording:
                        data = array(
                            "h",
                            self.stream.read(self.chunk, exception_on_overflow=False),
                        )
                        self.frames.append(data)

                        self.mean = sum([abs(item) for item in data]) / len(data)
            else:
                while self.continue_recording:
                    data = array(
                        "h", self.stream.read(self.chunk, exception_on_overflow=False)
                    )
                    self.frames.append(data)
                    self.mean = sum([abs(item) for item in data]) / len(data)
            self.recording_loop_terminated = True

        t = threading.Thread(target=to_do)
        t.start()
    
    def calculate_threshold(self, percent, trial_num=6, data_len=80000):
        thresholds = []

        for trial in range(1, trial_num+1):

            emgs = []
            while len(emgs) <= data_len:
                emgs.append(self.mean)
                print(f'Progress: trial {trial} of {trial_num} ({round((len(emgs)/data_len)*100, 2):>5}%)', end='\r')
            
            diff = max(emgs) - min(emgs)

            thresholds.append(min(emgs) + (percent/100)*diff)
        
        return sum(thresholds)/len(thresholds)

    def detect_signal(
        self,
        threshold=3000,
    ):
        self.means.append(self.mean)
        return sum(self.means[-2:]) / 2 >= threshold

    def terminate_recording(self):
        self.continue_recording = False

        while True:
            if self.recording_loop_terminated:
                break

        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()
        self.in_recording = False