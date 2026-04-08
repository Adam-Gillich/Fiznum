import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle

# ----------------------------------
# File location
# ----------------------------------

ecg_file = '/v/courses/2026-afizikanumerikusmdszerei12026.public/data/ecg.pkl'

# ----------------------------------
# Helper functions
# ----------------------------------


def read_pkl(filename):
    """
    This function reads the pickle file and extracts
    its contents in a more iterable way, all the while
    preserving the original keys as 'measurement indexes'.
    :param filename: File location
    :return: Restructured data
    """

    with open(filename, 'rb') as file:
        ecg = pickle.load(file)

    def append_segment(key, segment: dict):
        segment.update({'measurement_index': str(key)})
        return segment

    data = [append_segment(key, ecg[key]) for key in ecg.keys()]

    return data


def explore_ecg(data: dict):
    """
    Function for the exploration of
    the raw unprocessed data.
    :param data: Raw data dict[dict]
    """

    print(f'Length of data: {len(data.keys())}')
    print('--------------------------------------------------------------------------')
    for key in data.keys():
        print(f'Key: {key}')
        print(f'    Keys of Data at key ({key}):')
        for k in data[key].keys():
            print(f'        Key: {k: <10}, shape: {np.shape(data[key][k])}, first elements: {data[key][k][:4]}')
        print('-------------------------------------')


def explore_list(data: list[dict]):
    """
    Function for the exploration of
    the processed data.
    :param data: Processed data list[dict]
    """

    print(f'Length of data: {len(data)}')
    print('--------------------------------------------------------------------------')
    for i, segment in enumerate(data):
        print(f'Index: {i}')
        print(f'    Keys of Data at index {i}:')
        for key in segment.keys():
            print(f'        Key: {key: <10}, shape: {np.shape(segment[key])}, first elements: {segment[key][:4]}')
        print('-------------------------------------')


def FourierSpectrum(segment):
    """
    This function is for calculating the Fast Fourier Transform (fft)
    of one segment. After we have that we calculate the
    amplitude of the fft values, because we don't need
    the complex numbers. And we calculate the frequency,
    and of course convert it to bpm.
    :param segment: One ECG segment
    :return: frequency in bpm, amplitude of fft values
    """

    t_data = segment['t']
    signal = segment['signal']

    N = len(t_data)
    dt = t_data[1] - t_data[0]

    # Real FFT: only positive frequencies
    """
    Let's decode!
        fft: Fast Fourier Transform
        rfft: Real fft
        rfftfreq: Real fft Frequency
    """
    fft_vals = np.fft.rfft(signal)
    freq_hz = np.fft.rfftfreq(N, d=dt)

    # I don't care about the complex
    amplitudes = np.abs(fft_vals)
    freq_bpm = 60 * freq_hz

    return freq_bpm, amplitudes


# ----------------------------------
# Plot
# ----------------------------------


def SetTex():
    """
    Sets TeX fonts.
    """

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


class Plot:

    def __init__(self, data):
        self.data = data

        SetTex()

    def all_ecg(self, shift_by=1):
        """
        This function plots all the raw ECG segments.
        The waterfall effect can be changed by modifying
        the 'shift_by' parameter.
        :param shift_by: Shift value
        """

        plt.figure(figsize=(18, 6))
        # Stock shift
        shift = 0

        # Plot ECGs
        for segment in self.data:
            t_data = segment['t']
            signal = segment['signal'] + shift

            plt.plot(t_data, signal, '-')
            shift += shift_by

        # Limit the plot, so it fills the screen --------------------------
        limx = [min(np.min(segment['t']) for segment in self.data), max(np.max(segment['t']) for segment in self.data)]
        plt.xlim(limx)

        # Custom tick label -----------------------------------------------
        # Label them with their measurement index
        tick_labels = [segment['measurement_index'] for segment in self.data]

        yticks = np.arange(0, shift_by*len(self.data), shift_by)
        plt.yticks(yticks, tick_labels)

        # Annotate --------------------------------------------------------
        plt.title(r'\textbf{All the ECG segments}', fontsize=20)
        plt.xlabel(r'\textsc{time} [\,$sec$\,]', fontsize=18)
        plt.ylabel(r"\textsc{Signal's measurement index}", fontsize=18)

        plt.show()

    def all_spectra(self, shift_by=500):
        """
        This function plots all the fft transformed ECG segments.
        The waterfall effect can be changed by modifying
        the 'shift_by' parameter.
        :param shift_by: Shift value
        """

        plt.figure(figsize=(12, 9))
        # Stock shift
        shift = 0

        # Plot Fourier Transforms
        for segment in self.data:
            freq, fft_signal = FourierSpectrum(segment)

            mask = freq <= 300
            plt.plot(freq[mask], fft_signal[mask] + shift, '-')
            shift += shift_by

        # Limit the plot, so it fills the screen --------------------------
        def only_freq(segment):
            f, idc = FourierSpectrum(segment)
            return f[mask]

        limx = [min(np.min(only_freq(segment)) for segment in self.data), max(np.max(only_freq(segment)) for segment in self.data)]
        plt.xlim(limx)

        # Custom tick label -----------------------------------------------
        # Label them with their measurement index
        tick_labels = [segment['measurement_index'] for segment in self.data]

        yticks = np.arange(0, shift_by * len(self.data), shift_by)
        plt.yticks(yticks, tick_labels)

        # Annotate --------------------------------------------------------
        plt.title(r'\textbf{The Fourier spectrum of all ECG segments}', fontsize=20)
        plt.xlabel(r'\textsc{frequency} [\,$bpm$\,]', fontsize=18)
        plt.ylabel(r"\textsc{Signal's measurement index}", fontsize=18)

        plt.show()

    def dominant_bpm(self, annotate=False):
        """
        This function plots all the dominant frequencies
        of the segments, with their 'measurement index'.\n
        If the user wishes to see the exact values of the bars,
        then by flipping the 'annotate' parameter they can inspect them.
        :param annotate: If True, the dominant frequencies will be displayed at the top of the bars.
        """

        plt.figure(figsize=(12, 5))

        # Plot ------------------------------------------------------------
        def freq_max(segment, freq_lim=150):
            f, amp = FourierSpectrum(segment)
            mask = f <= freq_lim
            index = np.argmax(amp[mask])
            f_max = f[mask][index]
            return f_max

        indices = np.arange(0, len(self.data))
        domi_freq = [freq_max(segment) for segment in self.data]

        plt.bar(indices, domi_freq, color=mpl.colormaps['tab10'].colors)

        # Annotate
        if annotate:
            shift = 1
            for i, freq in enumerate(domi_freq):
                plt.text(i - 0.45, freq + shift, f'{freq:.2f}')

        # Custom tick label -----------------------------------------------
        # Label them with their measurement index
        tick_labels = [segment['measurement_index'] for segment in self.data]

        xticks = np.arange(0, len(self.data))
        plt.xticks(xticks, tick_labels)

        # Annotate --------------------------------------------------------
        plt.title(r'\textbf{Dominant frequencies per segments}', fontsize=20)
        plt.xlabel(r"\textsc{Signal's measurement index}", fontsize=18)
        plt.ylabel(r"\textsc{dominant frequency} [$bpm$]", fontsize=18)

        plt.show()


if __name__ == '__main__':
    dat = read_pkl(ecg_file)

    plot = Plot(dat)

    plot.all_ecg()
    plot.all_spectra()
    plot.dominant_bpm()
