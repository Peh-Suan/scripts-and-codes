import tgt # for importing TextGrid
from scipy.io import wavfile # for reading wav files
import numpy as np # for mathematical processing
from tqdm import tqdm # shows progress bar
import seaborn as sns # for plotting
import matplotlib.pyplot as plt # for plotting
plt.rcParams.update({"lines.linewidth": .3})
sns.set_palette("pastel")

class EGGProcessor():
    def __init__(self, data_files, textgrid_file=""):
        self.data = {}
        self.tgrd = None
        if textgrid_file:
            self.add_textgrid(textgrid_file)
        for data_name in data_files:
            self.sampling_frequency, self.data[data_name] = wavfile.read(data_files[data_name])
            
        self.data_len = len(self.data[list(self.data.keys())[0]])
        self.time = np.arange(0, self.data_len)/self.sampling_frequency
        self.interval_data = {}
    
    def change_data_name(self, original_name, target_name):
        assert original_name in self.data, f"`{original_name}` not found in the data."
        self.data[target_name] = self.data.pop(original_name)
    
    def add_textgrid(self, textgrid_file=""):
        self.tgrd = tgt.read_textgrid(textgrid_file)
        
    def get_intervals(self, interval_tier_name=""):
        assert self.tgrd is not None, "Please add the TextGrid first."
        if interval_tier_name:
            return self.tgrd.get_tier_by_name(interval_tier_name)
        else:
            return self.tgrd.tiers[0]
    
    def set_interval(self, interval):
        assert type(interval) is dict or type(interval) is tgt.core.Interval, "The interval should be a tgt.core.Interval or a dict containg \"start_time\", \"end_time\", and \"text\"."
        
        if type(interval) is dict:
            assert "start_time" in interval and "end_time" in interval and "text" in interval, "The interval dict should contain \"start_time\", \"end_time\", and \"text\"."
        if type(interval) is tgt.core.Interval:
            start_time, end_time = interval.start_time, interval.end_time

        if self.interval_data!={} and self.interval_data["start_time"]==start_time and self.interval_data["end_time"]==end_time: return
        self.interval_data = {"start_time": start_time, "end_time": end_time}
        
    def get_data_within_time(self, start_time, end_time, data_name, return_time=False):
        assert data_name in self.data, f"`{data_name}` not found."
        data = self.data[data_name]
        start_id = np.argmin(abs(self.time-start_time))
        end_id = np.argmin(abs(self.time-end_time))
        
        if return_time:
            return data[start_id:end_id], self.time[start_id:end_id]
        else:
            return data[start_id:end_id]

    def get_interval_data(self, data_name, return_time=False, save=True):
        assert self.interval_data!={}, "Please set the interval first."
        if data_name not in self.interval_data:
            data, time = self.get_data_within_time(self.interval_data["start_time"], self.interval_data["end_time"], data_name, True)
            if save:
                self.interval_data[data_name] = data
                self.interval_data["time"] = time
        else:
            data, time = self.interval_data[data_name], self.interval_data["time"]
        
        if return_time:
            return data, time
        return data
    
    def differentiate(self, data_name):
        assert data_name in self.data, f"`{data_name}` not found."
        return np.gradient(self.data[data_name])
    
    def highpass_filter(self, data_name, cutoff_freq=100, order=2):
        assert data_name in self.data, f"`{data_name}` not found."
        from scipy import signal

        b, a = signal.butter(order, cutoff_freq, btype="high", analog=False, fs=40000)

        return signal.filtfilt(b, a, self.data[data_name])

    def smooth(self, data_name, box_pts=30):
        assert data_name in self.data, f"`{data_name}` not found."
        data = self.data[data_name]

        box = np.ones(box_pts)/box_pts
        return np.convolve(data, box, mode="same")
    
    def add_data(self, datas):
        assert type(datas) is dict, "The data to be added should be in a dict. The key(s) are the name(s) of the data. The values are the data or the wave files."
        datas_to_add = {}
        for data_name in datas:
            if type(datas[data_name]) is str:
                sampling_frequency, data = wavfile.read(datas[data_name])
                assert sampling_frequency==self.sampling_frequency, f"The data to be added `{data_name}` and other data do not have the same smapling frequencies: {sampling_frequency} and {self.sampling_frequency}."
            else:
                data = datas[data_name]
            
            assert len(data)==self.data_len, f"The data to be added `{data_name}` and other data do not have the same lengths: {len(data)} and {self.data_len}."
            datas_to_add[data_name] = np.array(data)
        
        for data_name in datas_to_add:
            self.data[data_name] = np.array(datas_to_add[data_name])

    def delete_data(self, data_names):
        if type(data_names) is str: data_names = [data_names]
        to_delete = []
        for data_name in data_names:
            assert data_name in self.data, f"`{data_name}` not found."
            to_delete+=[data_name]
            
        assert len(set(to_delete)-set(self.data.keys()))==0, "You cannot delete every data. At leaset one data should be left."
            
        for data_name in to_delete:
            del self.data[data_name]
            if "cycles" in self.interval_data and data_name in self.interval_data["cycles"]:
                del self.interval_data["cycles"][data_name]
            if "cycle_data" in self.interval_data:
                if data_name in self.interval_data["cycle_data"]:
                    del self.interval_data["cycle_data"][data_name]
                
                for this_data_name in self.interval_data["cycle_data"]:
                    if data_name in self.interval_data["cycle_data"][this_data_name]:
                        del self.interval_data["cycle_data"][this_data_name][data_name]

    def _plot_data(self, data, time, return_plot, w, h):
        fig, axs = plt.subplots(len(data), 1, figsize=(w, h*len(data)), sharex=True)
        if len(data)==1:
            axs = [axs]
        
        for data_name, ax in zip(data, axs):
            sns.lineplot(
                ax=ax,
                x=time,
                y=data[data_name],
            )
            ax.set_ylabel(data_name)
        
        axs[-1].set_xlabel("time")
        fig.tight_layout()
        if return_plot: return fig
        
    def plot_data_within_time(self, start_time, end_time, data_names=None, return_plot=False, w=10, h=2):
        if type(data_names) is str:
            data_names = [data_names]
        if not data_names:
            data_names = list(self.data.keys())
            
        data = {}
        for data_name in data_names:
            assert data_name in self.data, f"`{data_name}` not found."
            data[data_name], time = self.get_data_within_time(start_time, end_time, data_name, return_time=True)
        
        fig = self._plot_data(data, time, return_plot=True, w=w, h=h)
        if return_plot:
            return fig
        
    def plot_interval_data(self, data_names=None, return_plot=False, w=10, h=2):
        if type(data_names) is str:
            data_names = [data_names]
        if not data_names:
            data_names = list(self.data.keys())
            
        data = {}
        for data_name in data_names:
            assert data_name in self.data, f"`{data_name}` not found."
            data[data_name], time = self.get_interval_data(data_name, return_time=True)
            
        fig = self._plot_data(data, time, return_plot=True, w=w, h=h)
        if return_plot:
            return fig
        
    def get_interval_egg_cycles(self, data_name, min_amp=600, save=True, return_cycles=False):
        assert self.interval_data!=None, "Please set the interval first."
        assert data_name in self.data, f"`{data_name}` not found."
        data, time = self.get_data_within_time(self.interval_data["start_time"], self.interval_data["end_time"], data_name, return_time=True)
        egg_cycles = []
        start, end = None, None

        max_value = -np.inf
        min_value = np.inf
        for idx in range(len(time)-1):
            if data[idx]<=0 and data[idx+1]>=0:
                if not start:
                    start = (time[idx]+time[idx+1])/2
                    
                else:
                    end = (time[idx]+time[idx+1])/2

                    if max_value-min_value>=min_amp:
                        egg_cycles+=[(start, end)]
            
                    start, end = end, None
                    max_value = 0
                    min_value = 0
            max_value = max([max_value, data[idx]])
            min_value = min([min_value, data[idx]])
        assert len(egg_cycles)>0, "No cycle is found in this interval. Consider decreasing the minimum cycle amplitude, or select a wider time range."
        print(f"{len(egg_cycles)} cycles found.")
        if save:
            if "cycles" not in self.interval_data:
                self.interval_data["cycles"] = {}

            self.interval_data["cycles"][data_name] = egg_cycles
            
        if return_cycles: return egg_cycles
    
    def get_interval_all_cycle_data(self, cycle_name, data_names=None, save=True, return_data=False):
        assert self.interval_data!={}, "Please set the interval first."
        assert "cycles" in self.interval_data and cycle_name in self.interval_data["cycles"], "Please get the EGG cycles first."
        if type(data_names) is str: data_names = [data_names]
        if data_names is None:
            data_names = list(self.data.keys())

        data_names+=["cycle", "time_point"]
        data = {}
        appended_data_names = []
        for data_name in data_names.copy():
            assert data_name in ["cycle", "time_point"] or data_name in self.data.keys(), f"`{data_name}` not found."
            if "cycle_data" not in self.interval_data or cycle_name not in self.interval_data["cycle_data"] or data_name not in self.interval_data["cycle_data"][cycle_name]:
                data[data_name] = np.array([])

            else:
                data[data_name] = self.interval_data["cycle_data"][cycle_name][data_name]
                appended_data_names+=[data_name]
                
                if len(set(data_names)-set(appended_data_names))==0:
                    if return_data: return data
                    else: return

        for cycle_idx, cycle in enumerate(tqdm(self.interval_data["cycles"][cycle_name])):
            start_time, end_time = cycle
            start_id = np.argmin(abs(self.time-start_time))
            end_id = np.argmin(abs(self.time-end_time))
            
            for data_name in set(data_names)-set(appended_data_names)-{"cycle", "time_point"}:

                cycle_data = self.data[data_name][start_id:end_id]
                data[data_name] = np.append(data[data_name], cycle_data)

            if len(appended_data_names)==0:
                data["cycle"] = np.append(data["cycle"], np.array([cycle_idx]*len(cycle_data)))
                data["time_point"] = np.append(data["time_point"], np.array(range(len(cycle_data))))
                
        if save:
            if "cycle_data" not in self.interval_data:
                self.interval_data["cycle_data"] = {}
            
            if cycle_name not in self.interval_data["cycle_data"]:
                self.interval_data["cycle_data"][cycle_name] = {}
            for data_name in data_names:
                if data_name not in self.interval_data["cycle_data"][cycle_name]:
                    self.interval_data["cycle_data"][cycle_name][data_name] = data[data_name]
            
        if return_data: return data
    
    def plot_interval_all_cycle_data(self, cycle_name, data_names=None, w=10, h=2, save=False):
        assert self.interval_data!={}, "Please set the interval first."

        if not data_names:
            data_names = list(self.data.keys())
        n_subplot = len(data_names)
        data = self.get_interval_all_cycle_data(cycle_name, data_names, return_data=True, save=save)

        fig, axs = plt.subplots(n_subplot, 1, figsize=(w, h*n_subplot), sharex=True)
        if n_subplot==1:
            axs = [axs]

        cmap = sns.color_palette("flare", as_cmap=True)

        norm = plt.Normalize(data["cycle"].min(), data["cycle"].max())
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)

        for data_name, ax in zip(data, axs):
            if data_name in ["time_point", "cycle"]: continue
            if len(set(data["cycle"]))==1:
                sns.lineplot(
                    ax=ax,
                    x=data["time_point"],
                    y=data[data_name]
                )
                ax.set_ylabel(data_name)
            
            else:
                sns.lineplot(
                    ax=ax,
                    x=data["time_point"],
                    y=data[data_name],
                    hue=data["cycle"],
                    palette=cmap
                )
                ax.set_ylabel(data_name)
                ax.get_legend().remove()
                cb = ax.figure.colorbar(sm, ax=ax)
                cb.outline.set_visible(False)
        
        fig.tight_layout()
        axs[-1].set_xlabel("time_point")
