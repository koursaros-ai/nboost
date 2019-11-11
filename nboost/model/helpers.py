import requests
import sys
import os
import tarfile

MODEL_PATHS = {
    "tf_bert_marco" : {
        "url" : "https://storage.googleapis.com/koursaros/bert_marco.tar.gz",
        "ckpt" : "bert_marco/bert_model.ckpt"
    }
}

def download_model(model, data_dir):
    link = MODEL_PATHS[model]['url']
    file_name = os.path.join(data_dir, MODEL_PATHS[model]['url'].split('/')[-1])
    with open(file_name, "wb") as f:
        print("Downloading %s" % file_name)
        response = requests.get(link, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()
    return file_name


def extract(archive, data_dir):
    print("Extracting %s" % archive)
    tar = tarfile.open(archive)
    tar.extractall(data_dir)
    tar.close()