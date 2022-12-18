import tarfile,os
import sys
import csv
import os
import re
from pydub import AudioSegment
from io import BytesIO
from audio_cut_out_silence import trim_and_replace_audio

def get_tar_file_names():
    with tarfile.open("D:/Slakh/slakh2100_flac_redux.tar") as tar:
        file_names = tar.getnames()
        return file_names

"""
# SAVING THE NAMES TO CSV (IN CASE NEEDED LATER)
with open('tar_file_names.csv',mode='w') as csvfile:
    w = csv.writer(csvfile)
    w.writerow(file_names)
"""

def extract_tar_file(file_name):
    with tarfile.open("D:/Slakh/slakh2100_flac_redux.tar") as tar:
        tar.extract(file_name)

def extract_midi(file_name):
    extract_tar_file(file_name)

def extract_wav(file_name):
    flac_file_name = re.sub(r"\.wav",r".flac", file_name)
    extract_tar_file(flac_file_name)
    new_flac_file_name = os.getcwd()+r"/slakh2100_flac_redux"+flac_file_name[20::]
    flac = AudioSegment.from_file(new_flac_file_name, 'flac')
    new_wav_file_name = re.sub(r"\.flac",r".wav",new_flac_file_name)
    flac.export(new_wav_file_name,format = "wav")
    os.remove(new_flac_file_name)
    trim_and_replace_audio(new_wav_file_name)

def delete_extracted_tar_file(path_name):
    print(path_name)
    try:
        folder_name, _ = os.path.split(path_name)
        os.remove(path_name)
    except:
        print("Error in deleting extracted tar file!") 
    
def create_manifest(match):
    tar_files = get_tar_file_names()
    training_list = [x for x in tar_files if match in x] # take file names with "train"/"test"/"val" in them
    training_list = [x for x in training_list if ("MIDI" not in x) and ("stems" not in x) and ("metadata" not in x)]
    new_list = []
    for x in training_list:
        number = re.findall(r'\d+', x) # Find the substrings that correspond to numbers 
        number = [x for x in number if x != '2100'] # Remove 
        for x in number:
            new_list.append(x)

    # Now, turn it into a matrix with the correct file names
    matrix = [["" for i in range(2)] for j in range(len(new_list))]
    i=0
    for file_number in new_list:
        matrix[i][0] = 'slakh2100_flac_redux/'+match+'/Track'+file_number+'/mix.wav'
        matrix[i][1] = 'slakh2100_flac_redux/'+match+'/Track'+file_number+'/all_src.abc'
        i = i+1

    # Write matrix into csv 
    with open(os.getcwd()+match+r"_slakh.csv",mode='w+',newline='') as csvfile:
        w = csv.writer(csvfile,delimiter=",")
        w.writerows(matrix)        

if __name__ == "__main__":
    create_manifest("train")
    create_manifest("validation")
    create_manifest("test")
