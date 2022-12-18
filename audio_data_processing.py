import numpy as np
import torch
import torchaudio
import madmom
from librosa import note_to_hz
from data_loader import load_audio

def process_audio_as_spect(audio_path):
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
    #    fs = madmom.audio.signal.FramedSignal(y, sample_rate=sample_rate, frame_size=n_fft, hop_size=hop_length)
    #    spect = madmom.audio.spectrogram.Spectrogram(fs, window=window)
    #elif self.input_format == 'cqt':
    #    S = librosa.cqt(y, sr=self.sample_rate, fmin=self.fmin, n_bins=self.num_octaves * self.bins_per_octave,
    #                    bins_per_octave=self.bins_per_octave, hop_length=self.hop_length, window=self.window)
    #    spect = np.abs(S)
    #    spect = spect.astype(np.float32)
    #    spect = spect.T # TxH
    #elif self.input_format == 'log':
    fs = madmom.audio.signal.FramedSignal(y, sample_rate=sample_rate, frame_size=n_fft, hop_size=hop_length)
    bin_freqs = madmom.audio.stft.fft_frequencies(num_fft_bins=n_fft // 2, sample_rate=sample_rate)
    bins_per_octave = 48
    min_note="C2"
    fmin = note_to_hz(min_note)
    num_octaves=6
    fmax = fmin * (2**num_octaves)
    fb = madmom.audio.filters.LogarithmicFilterbank(bin_freqs,
                                                             unique_filters=False,
                                                             norm_filters=True,
                                                             num_bands=bins_per_octave,
                                                             fmin=fmin,
                                                             fmax=fmax)
    spect = madmom.audio.spectrogram.FilteredSpectrogram(fs, window=window, filterbank=fb)
    
    # S = log(S+1)
    spect = np.log1p(spect)
    spect = torch.FloatTensor(spect)

    # Normalize
    mean = spect.mean()
    std = spect.std()
    spect.add_(-mean)
    spect.div_(std)
    # spect = spect[0:100,] # Delete this 
    #print("spect shape is: "+str(spect.size()))

    return spect

