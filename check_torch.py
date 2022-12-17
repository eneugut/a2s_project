import torch

print(torch.cuda.is_available())

num_of_gpus = torch.cuda.device_count()
print(num_of_gpus)

#pip3 install cuda-python==11.7
#pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
#conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia

#from cuda import cuda, nvrtc
#import numpy as np

import torch
import torch.cuda


if torch.cuda.is_available():
    # CUDA is available, so you can use GPU-specific tensor operations
    x = torch.randn(5, 5)
    x_gpu = x.cuda()
    y_gpu = x_gpu + 2
    print(y_gpu)