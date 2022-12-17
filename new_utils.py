from numpy import array
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
import torch
import numpy as np
import re

#path = './datasets/nottingham_database/nottingham_parsed.txt'

label_encoder = LabelEncoder()
onehot_encoder = OneHotEncoder(categories=['A','B','C'], sparse=False)

def get_encoded_data(data):
    """
    returns data in one hot encoding
    """
    print("One-Hot encoding data...")

    values = array(data)
    
    # integer encode 
    integer_encoded = label_encoder.fit_transform(values)

    # binary encode
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)

    # return encoded data as well as vocab size
    return integer_encoded
    #, len(onehot_encoded[0])
    
def integer_encode(data):
    """
    returns dataset encoded into integers
    """
    values = array(data)
    
    integer_encoded = label_encoder.fit_transform(values)
    return integer_encoded