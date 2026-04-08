import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy as sci
import cmocean

# ----------------------------------
# File location
# ----------------------------------

wav_file = '/v/courses/2026-afizikanumerikusmdszerei12026.public/data/wav3.wav'


# ----------------------------------
# Helper functions
# ----------------------------------


def read_wav_(filename, channels=False):
    """
    This function reads the wav file and selects
    only channel one of the data. If the user wishes
    the channel number of the data can be printed,
    by flipping the 'channels' parameter.
    :param filename: File location
    :param channels: If True the number of channels will be printed to the terminal
    :return: samplerate, only channel one of data
    """
    # In case I forgor:
    # This returns the sample rate and the numpy arrany
    # of the data, where every element can have multiple
    # elements, if there are more channels.
    samplerate, data = sci.io.wavfile.read(filename)

    samples = data[:, 0]

    if channels:
        print(f'The data has {data.shape[1]} {'channel' if data.shape[1] == 1 else 'channels'}')

    return samplerate, samples


def write_wav_(file_in, file_out='wav3_corrected.wav'):
    """
    This function writes the corrected wav file,
    using the first good note of the original file.
    :param file_in: The original file, used as a template.
    :param file_out: The corrected file's name
    """

    samplerate, data = sci.io.wavfile.read(file_in)

    original_dtype = data.dtype
    channels = data.shape[1]

    NOTE_NUMBER = 7  # From picture

    # -----------------------------------------------------------
    # Constants read off of the spectrogram
    LEADING_SILENCE = 2.30
    TIME_BETWEEN = 2.0
    # Thus
    NOTE_START = 2.30
    NOTE_END = 4.25  # The sound actually ends at this moment, thus we need the TIME_BETWEEN
    # -----------------------------------------------------------
    # Calculate the sample numbers from seconds
    note_start = int(NOTE_START * samplerate)
    note_end = int(NOTE_END * samplerate)
    note_length = note_end - note_start
    time_between = int(TIME_BETWEEN * samplerate)
    leading_silence = int(LEADING_SILENCE * samplerate)

    # Total length of the corrected file
    total_samples = leading_silence + NOTE_NUMBER * time_between

    # Empty out array
    out = np.zeros((total_samples, channels), dtype=np.float64)

    # Get the first note from original as template, then paste it 7 times after each other  // on both channels
    for channel in range(channels):
        template = data[note_start:note_end, channel]
        for i in range(NOTE_NUMBER):
            start = leading_silence + i * time_between
            out[start:(start + note_length), channel] = template

    # Find the bounds (/limitations) of int16 dtype
    max_val = np.iinfo(original_dtype).max
    min_val = np.iinfo(original_dtype).min
    # Clip the out signal with those limits, while converting it back to the original, in this case int16 dtype
    out_int = np.clip(out, min_val, max_val).astype(original_dtype)

    # Write the file
    sci.io.wavfile.write(file_out, samplerate, out_int)

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
    """This class does the plotting"""

    def __init__(self, samplerate, samples):
        self.samplerate = samplerate
        self.samples = samples

        SetTex()

    def spectrogram(self):
        """
        This function creates the first channel's spectrogram.
        """

        plt.figure(figsize=(12, 6))

        nperseg = int(np.sqrt(self.samplerate))

        frequencies, times, spectrogram = sci.signal.spectrogram(self.samples, self.samplerate, nperseg=nperseg)

        # Plot ----------------------------------------
        spec = plt.imshow(spectrogram, aspect='auto', origin='lower',
                          extent=[times[0], times[-1], frequencies[0], frequencies[-1]], cmap=cmocean.cm.thermal)
        plt.clim(0, np.percentile(spectrogram, 99))

        plt.axhline(392, c='r', label='The problematic note')

        plt.ylim(0, 1500)
        # Colorbar
        cbar = plt.colorbar(spec, pad=0.01, shrink=0.9)
        cbar.set_label(label=r'Power [$dB$]', size=16)

        # Annotate ----------------------------------------
        plt.title(r"\textbf{Spectrum of the piano notes}", fontsize=20)
        plt.xlabel(r'\textsc{time} [$sec$]', fontsize=16)
        plt.ylabel(r'\textsc{frequency} [$Hz$]', fontsize=16)
        plt.legend(bbox_to_anchor=[1.05, 1.09])
        plt.show()


if __name__ == '__main__':
    data = read_wav_(wav_file, True)

    plot = Plot(data[0], data[1])

    plot.spectrogram()

    # write_wav_(wav_file)
