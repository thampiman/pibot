import time
import argparse
from os.path import join
import listen as li
import speech as sp
from model import preprocess as prep

class Brain:
    def __init__(self, listen_file):
        self.listen_file = listen_file
        self.awake = False

    def is_awake(self):
        return self.awake

    def wake_command(self):
        return True

    def command_centre(self):
        # Offline Classifier to detect:
        # - Wake Command
        # - Background Noise
        # - Weather
        # - Latest News
        # - Turn On Light
        # - Turn Off Light
        # - Man Utd Fixtures
        # - Formula 1 Race
        # - Stop
        response = None
        mfcc = prep.wav2mfcc(self.listen_file)
        print(mfcc.shape)
        return response

    def process(self):
        response = self.command_centre()
        return response

def main(args):
    listen_file = join(args.store, 'listen.wav')
    listen = li.Listen()
    brain = Brain(listen_file=listen_file)
    speech = sp.Speech()

    num_asleep = 0
    while 1:
        listen.record_to_file(listen_file)
        response = brain.process()

        if response:
            speech.speak(response)

        if not brain.is_awake():
            num_asleep += 1
            if num_asleep > 10:
                time.sleep(60)
                num_asleep = 0
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PiBot Central')
    parser.add_argument('store', type=str, help='path to store all files')
    args = parser.parse_args()
    main(args)
