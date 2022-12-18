from urllib.parse import urlparse
import requests
import shutil
import os
import time


def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return local_filename





if __name__ == '__main__':
    download_file("https://zenodo.org/record/4599666/files/slakh2100_flac_redux.tar.gz?download=1","D:\\Slakh\\new-slakh\\slakh2100_chrome.tar.gz")
