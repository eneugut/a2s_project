import argparse
import configparser
import json
import numpy as np
from new_labeling import *
import torchaudio
import madmom
import librosa

config = configparser.ConfigParser()
config.read("configs/slakh.cfg")
model_name = config['train']['model']
model_conf = config[model_name]
audio_conf = config['audio']

with open('labels_slakh.json') as label_file:
    labels = json.load(label_file)


#train_dataset = SpectrogramDataset(audio_conf=audio_conf, manifest_filepath="train_slakh.csv", labels=labels)

#train_dataset.parse_transcript(transcript_path="/slakh-data/babyslakh_16k/Track00001/all_src.abc")


def parse_transcript(transcript_path):
    transcript_path = "C:/Users/WorkStation/Documents/GitHub/a2s_project" + transcript_path
    with open(transcript_path, 'r') as transcript_file:
        transcript = transcript_file.read()
    transcript = np.array(list(transcript))
    transcript = Labeling.encode(transcript)
    return transcript



#x = parse_transcript(transcript_path="/slakh-data/babyslakh_16k/Track00001/all_src.abc")
#print(x)




def load_audio(path, normalize=True):
    path = "C:/Users/WorkStation/Documents/GitHub/a2s_project" + path
    sound, _ = torchaudio.load(path) # , normalization=normalize
    sound = sound.numpy().T
    if len(sound.shape) > 1:
        if sound.shape[1] == 1:
            sound = sound.squeeze()
        else:
            sound = sound.mean(axis=1)  # multiple channels, average
    print(sound.shape)
    return sound

def parse_audio(audio_path):
    y = load_audio(audio_path)
    #if self.noiseInjector:
    #    add_noise = np.random.binomial(1, self.noise_prob)
    #    if add_noise:
    #        y = self.noiseInjector.inject_noise(y)
    
    sample_rate=16000
    window_size = 0.09288
    n_fft = int(sample_rate * window_size)
    window = np.hamming
    window_stride = 0.02322
    hop_length = int(sample_rate * window_stride)

    # Build spectrogram
    #if self.input_format == 'stft':
    fs = madmom.audio.signal.FramedSignal(y, sample_rate=sample_rate, frame_size=n_fft, hop_size=hop_length)
    print(type(fs))
    print(fs.size)
    spect = madmom.audio.spectrogram.Spectrogram(fs, window=window)
    #elif self.input_format == 'cqt':
    #    S = librosa.cqt(y, sr=self.sample_rate, fmin=self.fmin, n_bins=self.num_octaves * self.bins_per_octave,
    #                    bins_per_octave=self.bins_per_octave, hop_length=self.hop_length, window=self.window)
    #    spect = np.abs(S)
    #    spect = spect.astype(np.float32)
    #    spect = spect.T # TxH
    #elif self.input_format == 'log':
    #    fs = madmom.audio.signal.FramedSignal(y, sample_rate=self.sample_rate, frame_size=self.n_fft, hop_size=self.hop_length)
    #    spect = madmom.audio.spectrogram.FilteredSpectrogram(fs, window=self.window, filterbank=self.fb)
    
    print(spect.shape)

    # S = log(S+1)
    spect = np.log1p(spect)
    print(spect.shape)
    spect = torch.FloatTensor(spect)
    print(spect.size())

    # Normalize
    mean = spect.mean()
    std = spect.std()
    spect.add_(-mean)
    spect.div_(std)
    print(spect.size())

    return spect

x = parse_audio("/slakh-data/babyslakh_16k/Track00001/mix.wav")

