import tarfile,os
import sys
import csv

# READING IN THE TAR FILE 
with tarfile.open("D:/Slakh/slakh2100_flac_redux.tar") as tar:

    file_names = tar.getnames()
    print(len(file_names))

"""
# SAVING THE NAMES TO CSV (IN CASE NEEDED LATER)
with open('tar_file_names.csv',mode='w') as csvfile:
    w = csv.writer(csvfile)
    w.writerow(file_names)
"""

def get_tar_file(file_name):
    with tarfile.open("D:/Slakh/slakh2100_flac_redux.tar") as tar:
        file = tar.getmember(file_name)
        return file

file = get_tar_file("slakh2100_flac_redux/train/Track00805/all_src.mid")
print(file)

def get_tar_names_based_on_regex(file_name, regex): 
    pass


#for member in tar.getmembers():
    #print(member)
    #f=tar.extractfile(member)
    #content=f.read()
    #print ("%s has %d newlines" %(member, content.count("\n")))
    #print ("%s has %d spaces" % (member,content.count(" ")))
    #print ("%s has %d characters" % (member, len(content)))





#with tarfile.open("#slakh2100_flac_redux.tar", mode='r') as t:

""" 
'slakh2100_flac_redux/train/Track00612/MIDI/S01.mid', 
'slakh2100_flac_redux/train/Track00638/MIDI/S02.mid', 
'slakh2100_flac_redux/test/Track02023/stems/S06.flac', 
'slakh2100_flac_redux/train/Track00805/all_src.mid', 
'slakh2100_flac_redux/test/Track01896/stems/S06.flac',
'slakh2100_flac_redux/omitted/Track01953/stems/S09.flac', 
'slakh2100_flac_redux/omitted/Track01910/MIDI/S12.mid',
'slakh2100_flac_redux/train/Track00124/mix.flac',
'slakh2100_flac_redux/train/Track01175/MIDI/S05.mid',
'slakh2100_flac_redux/train/Track00271/metadata.yaml', 
'slakh2100_flac_redux/train/Track00748/metadata.yaml', 
'slakh2100_flac_redux/omitted/Track01872/MIDI/S09.mid',
'slakh2100_flac_redux/train/Track00211/stems/S10.flac',
'slakh2100_flac_redux/omitted/Track01079/MIDI/S02.mid', 
'slakh2100_flac_redux/train/Track00533/stems/S03.flac',
'slakh2100_flac_redux/train/Track01485/all_src.mid',
'slakh2100_flac_redux/omitted/Track01817/mix.flac',
'slakh2100_flac_redux/omitted/Track01596/stems/S08.flac', 
'slakh2100_flac_redux/train/Track00045/stems/S04.flac',
'slakh2100_flac_redux/train/Track00259/mix.flac', 
'slakh2100_flac_redux/train/Track00532/stems/S09.flac',
'slakh2100_flac_redux/train/Track00664/stems/S01.flac',
'slakh2100_flac_redux/train/Track01217/MIDI/S04.mid',
'slakh2100_flac_redux/test/Track01951/stems/S02.flac', 'slakh2100_flac_redux/validation/Track01539/MIDI/S04.mid', 'slakh2100_flac_redux/train/Track00176/stems/S02.flac', 'slakh2100_flac_redux/train/Track00663/stems/S07.flac'] 
"""