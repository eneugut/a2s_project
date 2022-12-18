import json
import numpy as np
import torch


with open('labels_slakh.json') as label_file:
    labels = json.load(label_file)


char_to_index = { char: index for (index, char) in enumerate(sorted(list(labels))) }
start_token = len(char_to_index)
end_token = len(char_to_index) + 1
char_to_index['SOS'] = start_token
char_to_index['EOS'] = end_token

index_to_char = { index: char for (char, index) in char_to_index.items() }

n_index = len(char_to_index)+1

class Labeling:
    def encode(values):
        values = np.array(values)
        values = np.array([char_to_index[char] for char in values])
        #values = np.eye(n_index)[values]
        return torch.IntTensor(values)

    def decode(values):
        #values = [np.where(r==1)[0][0] for r in values]
        values = np.array([index_to_char[index] for index in values])
        return values

