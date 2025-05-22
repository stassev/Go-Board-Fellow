#Copyright (C) Svetlin Tassev

# This file is part of Go Board Fellow

# Go Board Fellow is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later version

# Go Board Fellow is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details

# You should have received a copy of the GNU General Public License along 
# with Go Board Fellow. If not, see <https://www.gnu.org/licenses/>.

import sounddevice as sd
from scipy.io.wavfile import write
import string

SAMPLE_RATE = 44100  # CD quality
DURATION = 1       # seconds per recording

def record_and_save(filename, prompt):
    print(f"\n{prompt}")
    input("Press Enter and speak clearly...")
    print("Recording...")
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    write(filename, SAMPLE_RATE, recording)
    print(f"Saved to {filename}")

def main():
    # Letters a-u
    for letter in string.ascii_lowercase[:21]:  # 'a' to 'u'
        filename = f"{letter}.wav"
        record_and_save(filename, f"Please say the letter '{letter.upper()}'")

    # Numbers 1-19
    for number in range(1, 20):
        filename = f"{number}.wav"
        record_and_save(filename, f"Please say the number '{number}'")
    filename = "resign.wav"
    record_and_save(filename, f"Please say 'resign'")
    filename = "pass.wav"
    record_and_save(filename, f"Please say 'pass'")
if __name__ == "__main__":
    main()
