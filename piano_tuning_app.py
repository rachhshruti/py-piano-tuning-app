import glob
import json
import logging
import numpy as np
import os
from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
import sounddevice as sd
import sys
import wavio as wv


def read_piano_notes_frequency():
    with open('config/piano_notes_frequency.json', 'r') as file:
        piano_notes_dict = json.load(file)
    return piano_notes_dict


def record_note(sampling_freq, duration, output_file):
    # Start recorder with the given values of
    # duration and sample frequency
    recording = sd.rec(int(duration * sampling_freq),
                       samplerate=sampling_freq, channels=1)

    # Record audio for the given number of seconds
    sd.wait()

    # Convert the NumPy array to audio file
    wv.write(output_file, recording, sampling_freq, sampwidth=1)


def clean_recording_files():
    recording_files = glob.glob('recordings/*')
    for recording_file in recording_files:
        os.remove(recording_file)


def get_frequency_note(output_file):
    # Open the file and convert to mono
    sr, data = wavfile.read(output_file)
    if data.ndim > 1:
        data = data[:, 0]
    else:
        pass

    # Fourier Transform
    yf = rfft(data)
    xf = rfftfreq(len(data), 1 / sr)

    # Uncomment these to see the frequency spectrum as a plot
    # plt.plot(xf, np.abs(yf))
    # plt.show()

    # Get the most dominant frequency and return it
    idx = np.argmax(np.abs(yf))
    freq = xf[idx]
    return freq


def tune_piano_note(actual_note_frequency_to_tune):
    current_note_frequency = 0
    retries = 1
    while current_note_frequency != actual_note_frequency_to_tune:
        logging.info('Recording the note to tune, number of tries=%d..', retries)
        output_file = 'recordings/recording_' + str(retries) + ".wav"
        record_note(44100, 3, output_file)
        logging.info('Finding current frequency of the recorded note to tune..')
        current_note_frequency = get_frequency_note(output_file)
        logging.info('current note frequency=', current_note_frequency)
    clean_recording_files()


def set_logging_config():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)


if __name__ == '__main__':
    set_logging_config()
    logging.info('Loading the piano notes frequency dictionary for 88-key piano..')
    piano_notes_frequency_dict = read_piano_notes_frequency()
    logging.info('Loaded the piano notes frequency dictionary for 88-key piano')

    note_to_tune = sys.argv[1]
    if note_to_tune in piano_notes_frequency_dict:
        logging.info('Tuning the note %s to the right frequency %f', note_to_tune,
                     piano_notes_frequency_dict[note_to_tune])
        tune_piano_note(piano_notes_frequency_dict[note_to_tune])
        logging.info('Tuned the note %s successfully', note_to_tune)
    else:
        logging.error('Incorrect note to tune, please enter the correct note!')
