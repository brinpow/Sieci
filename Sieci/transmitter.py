import signals
import encoder
import pyaudio
import audio

TIME = 0.025
MESSAGE = "a"


def transmit(code, stream):
    audio_0 = signals.sample_maker(440, TIME)
    audio_1 = signals.sample_maker(880, TIME)
    for i in range(len(code)):
        if code[i]:
            audio.audio_write(stream, audio_1)
        else:
            audio.audio_write(stream, audio_0)


if __name__ == "__main__":
    i = input("Gdzie wysłać\n")
    if i == '0':
        pa = pyaudio.PyAudio()
        speaker = audio.speaker_open(pa)
        transmit(encoder.encode(1, 2, MESSAGE), speaker)
        pa.terminate()
    else:
        wf = audio.wave_open_write("code3.wav")
        audio.set_wave_file(wf)
        transmit(encoder.encode(1, 2, MESSAGE), wf)
        wf.close()
