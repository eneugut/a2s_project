import tar_utilities
import pretty_midi
import wave
from new_processing import *


#tar_utilities.extract_tar_file("slakh2100_flac_redux/train/Track00052/all_src.mid")

#midi_data = pretty_midi.PrettyMIDI()
#print(midi_data)


#tar_utilities.extract_midi("slakh2100_flac_redux/train/Track01434/all_src.mid")
#tar_utilities.extract_wav("slakh2100_flac_redux/train/Track01434/mix.wav")

#file_name = "C:\\Users\\WorkStation\\Documents\\GitHub\\a2s_project\\slakh2100_flac_redux\\train\\Track00052\\all_src.mid"
file_name = "C:\\Users\\WorkStation\\Documents\\GitHub\\a2s_project\\slakh2100_flac_redux\\train\\Track01434\\all_src.mid"
#file_name = "C:\\Users\\WorkStation\\Documents\\GitHub\\a2s_project\\slakh2100_flac_redux\\validation\\Track01690\\all_src.mid"
#midi_data = pretty_midi.PrettyMIDI(file_name)

wav_file_name = "C:\\Users\\WorkStation\\Documents\\GitHub\\a2s_project\\slakh2100_flac_redux\\train\\Track01434\\mix.wav"


"""
print("MID1")
print(midi_data.key_signature_changes)
print(midi_data.time_signature_changes)
"""

#mid2 = subset_midi_segment(file_name,200,205)

"""
print("MID2")
print(mid2.key_signature_changes)
print(mid2.time_signature_changes)
"""

#print("mid1")
#print(find_actual_start_time(midi_data))
#print(midi_data.get_end_time())

#print("mid2")
#print(find_actual_start_time(mid2))
#print(mid2.get_end_time())

#mid2.write("C:\\Users\\WorkStation\\Documents\\GitHub\\a2s_project\\slakh2100_flac_redux\\train\\Track01434\\all_src_extract2.mid")

new_file_path = re.sub(r"\.wav",r"-001.wav", wav_file_name)


#subset_audio_segment(wav_file_name, 0,10)
#trimmed_sound.export(new_file_path, format="wav")
from data_loader_test import parse_audio

x = parse_audio("/slakh-data/babyslakh_16k/Track00001/mix.wav")
print(x)