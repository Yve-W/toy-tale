import wave
import sys
import pyaudio

def play_wave_file(filename):
    CHUNK = 1024

    # Try to open the wave file; exit if it fails
    try:
        wf = wave.open(filename, 'rb')
    except FileNotFoundError:
        print(f"File {filename} not found.")
        sys.exit(-1)
    except wave.Error as e:
        print(f"Could not read file {filename}: {e}")
        sys.exit(-1)

    # Instantiate PyAudio and initialize PortAudio system resources
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Play samples from the wave file
    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

    # Close stream
    stream.close()
    wf.close()

    # Release PortAudio system resources
    p.terminate()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f'Plays a wave file. Usage: {sys.argv[0]} filename.wav')
        sys.exit(-1)

    # Play the specified wave file
    play_wave_file(sys.argv[1])
