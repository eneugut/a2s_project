import os
import sys
sys.path.insert(1, 'C:\\Users\\WorkStation\\Documents\\GitHub\\a2s_project\\EasyABC')
import midi2abc as m
import glob
import mido

# Root directory for slakh data
os.chdir('C:/Users/WorkStation/Documents/GitHub/a2s_project/slakh-data/babyslakh_16k')

# Converts midi file to abc file 
def midi_to_abc_and_write(input_file, output_file):
    abc = m.midi_to_abc(input_file)
    open(output_file, 'w').write(abc)

# Converts all .mid files to .abc: 
if __name__ == '__main__':

    mid = mido.MidiFile('./Track00001/all_src.mid')
    with open('./Track00001/all_src.csv', 'w') as file:
        for msg in mid.tracks[0]:
            file.write(str(msg))
            file.write('\n')

    #print(mid.length/60)
    #messages
    #print(mid.tracks[0].sort(key=lambda message: message.time))
    #times = []
    #for msg in mid.tracks[0]:
    #    print(msg)
    #    times.append(msg.time)
    #print(set(times))

    """
    for path in os.listdir():
        input_file = glob.glob(os.path.join(path,'*.mid'))[0]
        output_file = input_file.replace('.mid','.abc')
        print(output_file)
        midi_to_abc_and_write(input_file,output_file)
    """