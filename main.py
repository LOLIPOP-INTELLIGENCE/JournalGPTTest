import openai

import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import sys

openai.api_key = ''

def record_audio(filename):
    def callback(indata, frames, time, status):
        nonlocal data, stop_recording
        if status:
            print(status, file=sys.stderr)
        if stop_recording.is_set():
            raise sd.CallbackStop
        data.append(indata.copy())

    # Define the sample rate and query the device's max input channels
    sample_rate = 44100
    num_input_channels = sd.query_devices(None, 'input')['max_input_channels']

    try:
        data = []
        stop_recording = threading.Event()

        with sd.InputStream(samplerate=sample_rate, channels=num_input_channels, callback=callback):
            print("Recording started...")
            input("Press Enter to stop the recording...")
            stop_recording.set()

        # Concatenate all recorded audio data into one NumPy array
        audio_data = np.concatenate(data, axis=0)

        # Save the audio data to the specified file as WAV (because MP3 is not supported by soundfile)
        import soundfile as sf
        sf.write(filename, audio_data, sample_rate)

        print(f"Recording saved to {filename}")

    except Exception as ex:
        print(ex)

# Record and save the audio
record_audio("audio.wav")
audio_file = open("audio.wav", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)

print(transcript['text'])