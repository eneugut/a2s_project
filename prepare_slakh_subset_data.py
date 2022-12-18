from new_processing import *
import os
from convert_midi import midi_to_abc

def get_song_length(wav_file_path):
    song = AudioSegment.from_file(os.getcwd()+wav_file_path, format="wav")
    return(len(song)/1000)

def calculate_number_of_subsongs():
    pass

def divide_and_export_as_pkl(wav_file_path, midi_file_path, duration):
    song_length = get_song_length(wav_file_path)
    sections = int(song_length/duration)
    #print("There are "+str(sections)+" sections")
    
    sound_tensors = []
    abc_files = []
    temp_midi_path = re.sub(r"\.mid",r"_temp.mid", midi_file_path)
    for i in range(sections):
        start = i*duration
        end = (i+1)*duration

        # First, we process the audio
        sound_tensor = subset_audio_segment(wav_file_path,start,end)
        sound_tensors.append(sound_tensor)

        # Second, we process the transcript
        midi_subset = subset_midi_segment(midi_file_path,start,end)
        midi_subset.write(os.getcwd()+temp_midi_path)
        abc_file = midi_to_abc(temp_midi_path)
        abc_files.append(abc_file)
        os.remove(os.getcwd()+temp_midi_path)

    # Now combine and export as pickle
    number = re.findall(r'\d+', wav_file_path) # Find number from file name0
    number = [x for x in number if x != '2100'] # Remove 

    type = ""
    if re.search("train", wav_file_path) is not None:
        type = "train"
    if re.search("validation", wav_file_path) is not None:
        type = "validation"
    if re.search("test", wav_file_path) is not None:
        type = "test"

    for i in range(len(sound_tensors)):
        pickle_file_path = r"/slakh-data/processed-slakh/"+type+r"/p"+number[0]+r'-'+f'{i:03d}'+r'.pkl'
        output_pickle((sound_tensors[i],abc_files[i]), pickle_file_path)