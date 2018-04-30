import os
import platform

class Speech:
    def __init__(self):
        self.os_name = os.name
        self.platform_system = platform.system()

    def speak(self, text):
        if self.os_name == 'posix' and self.platform_system == 'Darwin': # Mac OS
            os.system('say %s' % text)

if __name__ == '__main__':
    speech = Speech()
    speech.speak('Hello, Ajay!')
