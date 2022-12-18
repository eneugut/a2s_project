import time
import pretty_midi
import wave
from pydub import AudioSegment
import tar_utilities




def find_actual_start_time(mid):
    start_time = 100
    for instrument in mid.instruments:
        for note in instrument.notes:
            if note.start < start_time:
                start_time = note.start

    return(start_time)


def extract_midi_segment(mid,start_sec,end_sec):
    # Adjust times based on actual time start of midi
    start_time = find_actual_start_time(mid)
    print(start_time)
    start_sec = start_sec + start_time
    end_sec = end_sec + start_time
    new_mid = pretty_midi.PrettyMIDI() # Create new midi object

    # Extract notes
    for instrument in mid.instruments:
        new_instrument = pretty_midi.Instrument(instrument.program, instrument.is_drum, pretty_midi.program_to_instrument_name(instrument.program))
        new_mid.instruments.append(new_instrument)
        for i in range(len(instrument.notes)):
            note = instrument.notes[i]
            if (note.start < start_sec and note.end < end_sec) or (note.start > end_sec):
                pass
            else: # Delete notes after end_sec
                new_mid.instruments[-1].notes.append(note)

    return new_mid

tar_utilities.extract_tar_file("slakh2100_flac_redux/train/Track00052/all_src.mid")
file_name = "C:\\Users\\WorkStation\\Documents\\GitHub\\a2s_project\\slakh2100_flac_redux\\train\\Track00052\\all_src.mid"

#midi_data = pretty_midi.PrettyMIDI()
midi_data = pretty_midi.PrettyMIDI(file_name)
print(midi_data)
audio = wave.open(r"C:\\Users\\WorkStation\\Documents\\GitHub\\a2s_project\\slakh-data\\babyslakh_16k\\Track00001\\mix.wav", 'r')

mid2 = extract_midi_segment(midi_data,100,110)
print(midi_data.get_end_time())
print(mid2.get_end_time())
print(find_actual_start_time(midi_data))
print(find_actual_start_time(mid2))


"""

frames = audio.getnframes()
rate = audio.getframerate()
duration = frames / float(rate)
print(duration)

for i in range(20):
    frame = audio.readframes(1)
    #print(frame)


silent_frames = []

for i in reversed(range(audio.getnframes())):
    ### read 1 frame and the position will updated ###
    frame = audio.readframes(1)

    all_zero = True
    for j in range(len(frame)):
        #print(frame[j])
        # check if amplitude is greater than 0
        if frame[j] > 0:
            all_zero = False
            break

    if all_zero:
        silent_frames.append((audio.tell()/audio.getframerate()))
        # perform your cut here
        #print ('silence found at frame %s' % audio.tell())
        #print ('silence found at second %s' % (audio.tell()/audio.getframerate()))

silent_frames =  [round(x,2) for x in silent_frames] 

print(sorted(set(silent_frames)))
"""

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0 # ms

    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

def trim_and_replace_audio(file_path):

    sound = AudioSegment.from_file(file_path, format="wav")

    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())

    duration = len(sound)    
    trimmed_sound = sound[start_trim:duration-end_trim]

    trimmed_sound.export(file_path, format="wav")

#trim_and_replace_audio(r"C:\\Users\\WorkStation\\Documents\\GitHub\\a2s_project\\slakh-data\\babyslakh_16k\\Track00001\\mix.wav")