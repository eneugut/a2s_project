from urllib.parse import urlparse
import requests
import shutil
import os
import time

"""
def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return local_filename
"""

def download_file(url, local_filename):
    for i in range(0,100):
        byte_start = int(i*1e9)
        byte_end = int((i+1)*1e9 - 1)
        byte_range = f'bytes='+str(byte_start)+f'-'+str(byte_end)
        header = {'Range':byte_range}
        r = requests.get(url, stream=True,headers = header)
        new_filename = local_filename + str(i)
        with open(new_filename, 'wb') as file:
            for chunk in r:
                file.write(chunk)
        print("Downloaded file "+new_filename)

""" def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename
 """

""" def download_file(url: str, file_path='', attempts=2):
    Downloads a URL content into a file (with large file support by streaming)

    :param url: URL to download
    :param file_path: Local file name to contain the data downloaded
    :param attempts: Number of attempts
    :return: New file path. Empty string if the download failed
    
    if not file_path:
        file_path = os.path.realpath(os.path.basename(url))
    print(f'Downloading {url} content to {file_path}')
    url_sections = urlparse(url)
    if not url_sections.scheme:
        print('The given url is missing a scheme. Adding http scheme')
        url = f'http://{url}'
        print(f'New url: {url}')
    chunk_num = 0
    start_time = time.time()
    for attempt in range(1, attempts+1):
        try:
            if attempt > 1:
                time.sleep(10)  # 10 seconds wait time between downloads
            with requests.get(url, stream=True,headers = {'Range':'bytes=0-2000000'}) as response:
                response.raise_for_status()
                with open(file_path, 'ab') as out_file:
                    for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                        out_file.write(chunk)
                        chunk_num = chunk_num + 1
                        if (chunk_num % 100 == 0):
                            end_time = time.time()
                            print("Chunk number: "+str(chunk_num))
                            print(end_time - start_time)
                            start_time = end_time
                print('Download finished successfully')
                return file_path
        except Exception as ex:
            print(f'Attempt #{attempt} failed with error: {ex}')
    return ''
 """


if __name__ == '__main__':
    download_file("https://zenodo.org/record/4599666/files/slakh2100_flac_redux.tar.gz?download=1","D:\\Slakh\\new-slakh\\slakh2100.part.")
