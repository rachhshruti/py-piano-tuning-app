# Piano Tuning App in Python

## Pre-requisites
- Python 3

## Install Dependencies
```shell
    brew install portaudio
    pip3 install -r requirements.txt
```

## Running the app
```shell
    python3 piano_tuning_app.py
```

## Future ideas for automatic transcription
### Tempo detection in bpm (beats per minute)
https://www.reddit.com/r/audioengineering/comments/196ysgu/bpm_detection_algorithm_help/
- Tempo detection is a hard problem in the general case, but in narrow cases you can take some shortcuts, as you're 
discovering.

If you can assume that
- The loops are already cut at bar boundaries
- Loops are short (1-8 bars)
- The time signature is 4/4 (let's face it, 99% of western music is)
- Most music's tempos are within 60 - 200bpm

Then you can take the length in seconds, calculate the tempo if the loop were 1 bar, 2 bars, 4 bars or 8 bars, and pick 
the most likely bar length / tempo. Let's say you have a 6 second loop - let's see what the options are for bar length 
and tempos:

1 bar -> (4 beats / 6 seconds) * (60 seconds / minute) = 40 beats per minute

2 bars -> (8 beats / 6 seconds) * (60 seconds / minute) = 80 beats per minute

4 bars -> (16 beats / 6 seconds) * (60 seconds / minute) = 160 beats per minute

8 bars -> (32 beats / 6 seconds) * (60 seconds / minute) = 320 beats per minute

Since 40bpm is too low and 320bpm is too high, we can be confident this is either a 2 bar / 80 bpm loop or a 
4 bar / 160 bpm. I could just pick one randomly, or if you get fancier you could have it know that there's more 80bpm 
music than 160bpm music, so 80 is the best choice.


### Time signature detection based on tempo

### Scale detection

### Individual notes and chords detection
