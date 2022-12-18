from prepare_slakh_subset_data import *
from new_processing import input_pickle

wav_file_name = "/slakh2100_flac_redux/train/Track01434/mix.wav"
midi_file_name = "/slakh2100_flac_redux/train/Track01434/all_src.mid"



divide_and_export_as_pkl(wav_file_name, midi_file_name,8)

x = input_pickle("\slakh-data\processed-slakh/train\p01434-000.pkl")
