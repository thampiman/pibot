from sys import byteorder
from array import array
from struct import pack

import pyaudio
import wave

class Listen:
    def __init__(self, threshold=700, chunk_size=1024, 
                 rate=44100, maximum=16384, num_channels=1,
                 num_silent_max=30, num_pad=0.5):
        self.threshold = threshold
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        self.rate = rate
        self.maximum = maximum
        self.num_channels = 1
        self.num_silent_max = num_silent_max
        self.num_pad = num_pad

    def is_silent(self, snd_data):
        "Returns 'True' if below the 'silent' threshold"
        return max(snd_data) < self.threshold

    def normalise(self, snd_data):
        "Average the volume out"
        times = float(self.maximum) / max(abs(i) for i in snd_data)
        r = array('h')
        for i in snd_data:
            r.append(int(i * times))
        return r

    def trim(self, snd_data):
        "Trim the blank spots at the start and end"
        def _trim(snd_data, threshold):
            snd_started = False
            r = array('h')
            for i in snd_data:
                if not snd_started and abs(i) > threshold:
                    snd_started = True
                    r.append(i)
                elif snd_started:
                    r.append(i)
            return r

        # Trim to the left
        snd_data = _trim(snd_data, self.threshold)

        # Trim to the right
        snd_data.reverse()
        snd_data = _trim(snd_data, self.threshold)
        snd_data.reverse()
        return snd_data

    def add_silence(self, snd_data, second):
        "Add silence to the start and end of 'snd_data'"
        r = array('h', [0 for i in range(int(second * self.rate))])
        r.extend(snd_data)
        r.extend([0 for i in range(int(second * self.rate))])
        return r

    def record(self):
        """
        Record a word or words from the microphone and 
        return the data as an array of signed shorts.

        Normalises the audio, trims silence from the
        start and end, and pads with 'num_pad' seconds of
        blank sound to make sure any player can play 
        it without getting chopped off.
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format, channels=self.num_channels, 
            rate=self.rate, input=True, output=True, 
            frames_per_buffer=self.chunk_size)
        num_silent = 0
        snd_started = False
        r = array('h')

        while 1:
            # little endian, signed short
            snd_data = array('h', stream.read(self.chunk_size))
            if byteorder == 'big':
                snd_data.byteswap()
            r.extend(snd_data)

            silent = self.is_silent(snd_data)
            if silent and snd_started:
                num_silent += 1
            elif not silent and not snd_started:
                snd_started = True

            if snd_started and num_silent > self.num_silent_max:
                break

        sample_width = p.get_sample_size(self.format)
        stream.stop_stream()
        stream.close()
        p.terminate()

        r = self.normalise(r)
        r = self.trim(r)
        r = self.add_silence(r, self.num_pad)
        return sample_width, r

    def record_to_file(self, path):
        "Records from the microphone and outputs the resulting data to 'path'"
        sample_width, data = self.record()
        data = pack('<' + ('h' * len(data)), *data)

        wf = wave.open(path, 'wb')
        wf.setnchannels(self.num_channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(self.rate)
        wf.writeframes(data)
        wf.close()

if __name__ == '__main__':
    print('Please speak into the microphone. Recording will stop when there is a pause...')
    listen = Listen()
    filename = '/Users/ajay/Desktop/demo.wav'
    listen.record_to_file(filename)
    print('Done! File saved at %s' % filename)
