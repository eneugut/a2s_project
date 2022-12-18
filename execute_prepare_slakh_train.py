from prepare_slakh_subset_data import *
from new_processing import input_pickle
import csv
from tar_utilities import extract_midi, extract_wav, delete_extracted_tar_file

with open(os.getcwd()+r"\\train_slakh.csv",mode='r',newline='') as csvfile:
    csv = csv.reader(csvfile)
    i = 0
    for row in csv:
        wav_file_name = row[0]
        midi_file_name = re.sub(r"\.abc",r".mid", row[1])
        extract_wav(wav_file_name)
        extract_midi(midi_file_name)
        divide_and_export_as_pkl(r"/"+wav_file_name, r"/"+midi_file_name,8)
        delete_extracted_tar_file(os.getcwd()+r"/"+wav_file_name)
        delete_extracted_tar_file(os.getcwd()+r"/"+midi_file_name)
        print(i)
        i = i+1
