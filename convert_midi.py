import os
import sys
sys.path.insert(1, 'C:\\Users\\WorkStation\\Documents\\GitHub\\a2s_project\\EasyABC')
import midi2abc as m
import glob
import mido

# Converts midi file to abc file 
def midi_to_abc_and_write(input_file, output_file):
    abc = m.midi_to_abc(input_file)
    open(output_file, 'w').write(abc)

def midi_to_abc(midi_file_path):
    abc = m.midi_to_abc(os.getcwd()+midi_file_path)
    return(abc)

# Converts all .mid files to .abc: 
if __name__ == '__main__':

    """
    for path in os.listdir():
        input_file = glob.glob(os.path.join(path,'*.mid'))[0]
        output_file = input_file.replace('.mid','.abc')
        print(output_file)
        midi_to_abc_and_write(input_file,output_file)
    """