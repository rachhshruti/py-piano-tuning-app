import glob
import json
import logging
import numpy as np
import os
import pyaudio
from scipy.fft import fft, fftfreq
import sys
import wave


def read_piano_notes_frequency():
    '''
    Reads the list of piano notes and it's frequencies from json file
    :return: dictionary of piano notes frequencies
    '''
    with open('config/piano_notes_frequency.json', 'r') as file:
        piano_notes_dict = json.load(file)
    return piano_notes_dict


def record_note(sampling_freq, chunk_size, output_file, duration=3):
    '''
    Records the note for fixed duration and saves in .wav file
    :param sampling_freq: sampling frequency is the number of times per second that an analog audio signal is sampled to
    create a digital file. Example, 44100 is the standard sample rate for most consumer audio, like CDs.
    :param chunk_size: chunk size refers to the amount of audio data that is processed and stored together as a single
    unit
    :param output_file: name of .wav file to store the recording
    :param duration: duration of the recording in seconds, default is 3 seconds.
    '''
    audio_format = pyaudio.paInt16
    channels = 1
    p = pyaudio.PyAudio()

    stream = p.open(format=audio_format,
                    channels=channels,
                    rate=sampling_freq,
                    input=True,
                    frames_per_buffer=chunk_size)

    logging.info("Recording for duration of %d seconds...", duration)
    frames = []

    for i in range(0, int(sampling_freq / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    logging.info("Finished recording")

    wf = wave.open(output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(audio_format))
    wf.setframerate(sampling_freq)
    wf.writeframes(b''.join(frames))
    wf.close()


def clean_recording_files():
    '''
    Deletes/cleans up .wav files used for storing piano note recording after a note is successfully tuned.
    '''
    recording_files = glob.glob('recordings/*')
    for recording_file in recording_files:
        os.remove(recording_file)


def read_wav_file(filename):
    '''
    Reads wav file that stores a single note that is being tuned.
    :param filename: name of the .wav file
    :return: audio data and sampling_frequency
    '''
    with wave.open(filename, 'rb') as wav_file:
        sampling_frequency = wav_file.getframerate()
        nframes = wav_file.getnframes()

        # Read the audio data
        audio_data = wav_file.readframes(nframes)

        audio_data = np.frombuffer(audio_data, dtype=np.int16)

        return audio_data, sampling_frequency


def get_frequency_note(output_file, duration=3):
    '''
    Finds frequency of the note from the .wav file
    :param output_file: name of wav file that has recording of single note
    :param duration: duration of the audio should be same as above when recording the note, default is 3 seconds
    :return: frequency of note to be tuned
    '''
    data, sr = read_wav_file(output_file)

    # Fourier Transform
    yf = fft(data[:sr*duration])
    xf = fftfreq(sr*duration, 1 / sr)

    # Get the most dominant frequency and return it
    idx = np.argmax(np.abs(yf))
    freq = xf[idx]
    return freq


def tune_piano_note(actual_note_frequency_to_tune):
    '''
    Tune the piano note passed as command line argument. Records the note to be tuned, finds it's frequency and then
    compares it to actual frequency and until the two frequencies does not match, it repeats these steps.
    Cleans the recording files once the note is successfully tuned.
    :param actual_note_frequency_to_tune: actual frequency of the note to be tuned
    '''
    current_note_frequency = 0
    retries = 1
    while current_note_frequency != actual_note_frequency_to_tune:
        logging.info('Recording the note to tune, number of tries=%d..', retries)
        output_file = 'recordings/recording_' + str(retries) + ".wav"
        record_note(44100, 1024, output_file)
        logging.info('Finding current frequency of the recorded note to tune..')
        current_note_frequency = get_frequency_note(output_file)
        logging.info('current note frequency=%f', current_note_frequency)
        retries = retries + 1
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
