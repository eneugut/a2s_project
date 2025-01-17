import os
import subprocess
import pickle
from tempfile import NamedTemporaryFile
from pathlib import Path
import time

from torch.distributed import get_rank
from torch.distributed import get_world_size
from torch.utils.data.sampler import Sampler

import librosa
import madmom
import numpy as np
import scipy.signal
import torch
import torchaudio
import math
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from new_labeling import Labeling

from utils import pad_list, IGNORE_ID

windows = {'hamming': np.hamming, 'hanning': np.hanning, 'blackman': np.blackman, 'bartlett': np.bartlett}

def load_audio(path, normalize=True):
    path = os.getcwd() + path
    sound, _ = torchaudio.load(path) # , normalization=normalize
    sound = sound.numpy().T
    if len(sound.shape) > 1:
        if sound.shape[1] == 1:
            sound = sound.squeeze()
        else:
            sound = sound.mean(axis=1)  # multiple channels, average
    return sound


class AudioParser(object):
    def parse_transcript(self, transcript_path):
        """
        :param transcript_path: Path where transcript is stored from the manifest file
        :return: Transcript in training/testing format
        """
        raise NotImplementedError

    def parse_audio(self, audio_path):
        """
        :param audio_path: Path where audio is stored from the manifest file
        :return: Audio in training/testing format
        """
        raise NotImplementedError


class NoiseInjection(object):
    def __init__(self,
                 path=None,
                 sample_rate=16000,
                 noise_levels=(0, 0.5)):
        """
        Adds noise to an input signal with specific SNR. Higher the noise level, the more noise added.
        Modified code from https://github.com/willfrey/audio/blob/master/torchaudio/transforms.py
        """
        if not os.path.exists(path):
            print("Directory doesn't exist: {}".format(path))
            raise IOError
        self.paths = path is not None and librosa.util.find_files(path)
        self.sample_rate = sample_rate
        self.noise_levels = noise_levels

    def inject_noise(self, data):
        noise_path = np.random.choice(self.paths)
        noise_level = np.random.uniform(*self.noise_levels)
        return self.inject_noise_sample(data, noise_path, noise_level)

    def inject_noise_sample(self, data, noise_path, noise_level):
        noise_len = get_audio_length(noise_path)
        data_len = len(data) / self.sample_rate
        noise_start = np.random.rand() * (noise_len - data_len)
        noise_end = noise_start + data_len
        noise_dst = audio_with_sox(noise_path, self.sample_rate, noise_start, noise_end)
        assert len(data) == len(noise_dst)
        noise_energy = np.sqrt(noise_dst.dot(noise_dst) / noise_dst.size)
        data_energy = np.sqrt(data.dot(data) / data.size)
        data += noise_level * noise_dst * data_energy / noise_energy
        return data


class SpectrogramParser(AudioParser):
    def __init__(self, audio_conf):
        """
        Parses audio file into spectrogram with optional normalization and various augmentations
        :param audio_conf: Dictionary containing the sample rate, window and the window length/stride in seconds
        :param normalize(default False):  Apply standard mean and deviation normalization to audio tensor
        :param augment(default False):  Apply random tempo and gain perturbations
        """
        super(SpectrogramParser, self).__init__()
        self.input_format = audio_conf.get('input_format', 'stft')
        self.sample_rate = audio_conf.getint('sample_rate', 22050)
        self.window_size = audio_conf.getfloat('window_size', 0.09288)
        self.window_stride = audio_conf.getfloat('window_stride', 0.02322)
        self.window = windows.get(audio_conf['window'], windows['hamming'])
        self.min_note = audio_conf.get('min_note')
        self.num_octaves = audio_conf.getint('num_octaves')
        self.bins_per_octave = audio_conf.getint('bins_per_octave')
        self.normalize = audio_conf.getboolean('normalize', True)
        self.augment = audio_conf.getboolean('augment', False)
        self.noiseInjector = NoiseInjection(audio_conf['noise_dir'], self.sample_rate,
                                            audio_conf['noise_levels']) if audio_conf.get('noise_dir') is not None else None
        self.noise_prob = audio_conf.get('noise_prob')
        self.n_fft = int(self.sample_rate * self.window_size)
        self.hop_length = int(self.sample_rate * self.window_stride)

        self.fmin = librosa.note_to_hz(self.min_note)
        self.fmax = self.fmin * (2**self.num_octaves)
        bin_freqs = madmom.audio.stft.fft_frequencies(num_fft_bins=self.n_fft // 2, sample_rate=self.sample_rate)
        self.fb = madmom.audio.filters.LogarithmicFilterbank(bin_freqs,
                                                             unique_filters=False,
                                                             norm_filters=True,
                                                             num_bands=self.bins_per_octave,
                                                             fmin=self.fmin,
                                                             fmax=self.fmax)

    def parse_audio(self, audio_path):
        if self.augment:
            y = load_randomly_augmented_audio(audio_path, self.sample_rate)
        else:
            y = load_audio(audio_path)
        if self.noiseInjector:
            add_noise = np.random.binomial(1, self.noise_prob)
            if add_noise:
                y = self.noiseInjector.inject_noise(y)
        # Build spectrogram
        if self.input_format == 'stft':
            fs = madmom.audio.signal.FramedSignal(y, sample_rate=self.sample_rate, frame_size=self.n_fft, hop_size=self.hop_length)
            spect = madmom.audio.spectrogram.Spectrogram(fs, window=self.window)
        elif self.input_format == 'cqt':
            S = librosa.cqt(y, sr=self.sample_rate, fmin=self.fmin, n_bins=self.num_octaves * self.bins_per_octave,
                            bins_per_octave=self.bins_per_octave, hop_length=self.hop_length, window=self.window)
            spect = np.abs(S)
            spect = spect.astype(np.float32)
            spect = spect.T # TxH
        elif self.input_format == 'log':
            fs = madmom.audio.signal.FramedSignal(y, sample_rate=self.sample_rate, frame_size=self.n_fft, hop_size=self.hop_length)
            spect = madmom.audio.spectrogram.FilteredSpectrogram(fs, window=self.window, filterbank=self.fb)

        # S = log(S+1)
        spect = np.log1p(spect)
        spect = torch.FloatTensor(spect)
        if self.normalize:
            mean = spect.mean()
            std = spect.std()
            spect.add_(-mean)
            spect.div_(std)
            #spect = spect[0:100,] # INSERTED THIS HERE TO CUT OFF THE SIZE OF THE AUDIO -- NEED TO FIX THIS LATER

        return spect

    def parse_transcript(self, transcript_path):
        raise NotImplementedError


class SpectrogramDataset(Dataset, SpectrogramParser):
    def __init__(self, audio_conf, manifest_filepath, labels):
        """
        Dataset that loads tensors via a csv containing file paths to audio files and transcripts separated by
        a comma. Each new line is a different sample. Example below:

        /path/to/audio.wav,/path/to/audio.txt
        ...

        :param audio_conf: Dictionary containing the sample rate, window and the window length/stride in seconds
        :param manifest_filepath: Path to manifest csv as describe above
        :param labels: String containing all the possible characters to map to
        :param normalize: Apply standard mean and deviation normalization to audio tensor
        :param augment(default False):  Apply random tempo and gain perturbations
        """
        with open(manifest_filepath) as f:
            ids = f.readlines()
        ids = [x.strip().split(',') for x in ids]
        self.ids = ids
        self.size = len(ids)
        self.labels_map = dict([(labels[i], i) for i in range(len(labels))])
        super(SpectrogramDataset, self).__init__(audio_conf)

    def __getitem__(self, index):
        sample = self.ids[index]
        audio_path, transcript_path = sample[0], sample[1]
        spect = self.parse_audio(audio_path)
        transcript = self.parse_transcript(transcript_path)
        return spect, transcript, transcript_path

    def parse_transcript(self, transcript_path):
        transcript_path = os.getcwd() + transcript_path
        with open(transcript_path, 'r') as transcript_file:
            transcript = transcript_file.read()
        transcript = np.array(list(transcript))
        #transcript = transcript[:30] # Limit transcript size
        transcript = Labeling.encode(transcript)
        return transcript

    def __len__(self):
        return self.size


def _collate_fn(batch):
    batch = sorted(batch, key=lambda sample: sample[0].size(0), reverse=True)
    inputs = []
    targets = []
    input_sizes = torch.IntTensor(len(batch))
    target_sizes = torch.IntTensor(len(batch))
    filenames = []
    for i, sample in enumerate(batch):
        spect, target, filename = sample
        inputs.append(spect)
        targets.append(target)
        input_sizes[i] = spect.size(0)
        target_sizes[i] = len(target)
        filenames.append(filename)
    inputs = pad_list(inputs, 0)
    targets = pad_list(targets, IGNORE_ID)
    return inputs, targets, input_sizes, target_sizes, filenames


class AudioDataLoader(DataLoader):
    def __init__(self, *args, **kwargs):
        """
        Creates a data loader for AudioDatasets.
        """
        super(AudioDataLoader, self).__init__(*args, **kwargs)
        self.collate_fn = _collate_fn


class BucketingSampler(Sampler):
    def __init__(self, data_source, batch_size=1):
        """
        Samples batches assuming they are in order of size to batch similarly sized samples together.
        """
        super(BucketingSampler, self).__init__(data_source)
        self.data_source = data_source
        ids = list(range(0, len(data_source)))
        self.bins = [ids[i:i + batch_size] for i in range(0, len(ids), batch_size)]

    def __iter__(self):
        for ids in self.bins:
            yield ids

    def __len__(self):
        return len(self.bins)

    def shuffle(self, epoch):
        np.random.shuffle(self.bins)


class DistributedBucketingSampler(Sampler):
    def __init__(self, data_source, batch_size=1, num_replicas=None, rank=None):
        """
        Samples batches assuming they are in order of size to batch similarly sized samples together.
        """
        super(DistributedBucketingSampler, self).__init__(data_source)
        if num_replicas is None:
            num_replicas = get_world_size()
        if rank is None:
            rank = get_rank()
        self.data_source = data_source
        self.ids = list(range(0, len(data_source)))
        self.batch_size = batch_size
        self.bins = [self.ids[i:i + batch_size] for i in range(0, len(self.ids), batch_size)]
        self.num_replicas = num_replicas
        self.rank = rank
        self.num_samples = int(math.ceil(len(self.bins) * 1.0 / self.num_replicas))
        self.total_size = self.num_samples * self.num_replicas

    def __iter__(self):
        offset = self.rank
        # add extra samples to make it evenly divisible
        bins = self.bins + self.bins[:(self.total_size - len(self.bins))]
        assert len(bins) == self.total_size
        samples = bins[offset::self.num_replicas]  # Get every Nth bin, starting from rank
        return iter(samples)

    def __len__(self):
        return self.num_samples

    def shuffle(self, epoch):
        # deterministically shuffle based on epoch
        g = torch.Generator()
        g.manual_seed(epoch)
        bin_ids = list(torch.randperm(len(self.bins), generator=g))
        self.bins = [self.bins[i] for i in bin_ids]


def get_audio_length(path):
    output = subprocess.check_output(['soxi -D \"%s\"' % path.strip()], shell=True)
    return float(output)


def audio_with_sox(path, sample_rate, start_time, end_time):
    """
    crop and resample the recording with sox and loads it.
    """
    with NamedTemporaryFile(suffix=".wav") as tar_file:
        tar_filename = tar_file.name
        sox_params = "sox \"{}\" -r {} -c 1 -b 16 -e si {} trim {} ={} >/dev/null 2>&1".format(path, sample_rate,
                                                                                               tar_filename, start_time,
                                                                                               end_time)
        os.system(sox_params)
        y = load_audio(tar_filename)
        return y


def augment_audio_with_sox(path, sample_rate, tempo, gain):
    """
    Changes tempo and gain of the recording with sox and loads it.
    """
    with NamedTemporaryFile(suffix=".wav") as augmented_file:
        augmented_filename = augmented_file.name
        sox_augment_params = ["tempo", "{:.3f}".format(tempo)] #, "gain", "{:.3f}".format(gain)]
        sox_params = "sox \"{}\" -r {} -c 1 -b 16 -e si {} {} >/dev/null 2>&1".format(path, sample_rate,
                                                                                      augmented_filename,
                                                                                      " ".join(sox_augment_params))
        os.system(sox_params)
        y = load_audio(augmented_filename)
        return y


def load_randomly_augmented_audio(path, sample_rate=22050, tempo_range=(0.8, 1.2),
                                  gain_range=(0, 0)):
    """
    Picks tempo and gain uniformly, applies it to the utterance by using sox utility.
    Returns the augmented utterance.
    """
    low_tempo, high_tempo = tempo_range
    tempo_value = np.random.uniform(low=low_tempo, high=high_tempo)
    low_gain, high_gain = gain_range
    gain_value = np.random.uniform(low=low_gain, high=high_gain)
    audio = augment_audio_with_sox(path=path, sample_rate=sample_rate,
                                   tempo=tempo_value, gain=gain_value)
    return audio
