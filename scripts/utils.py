import io
import base64
import unicodedata
import re

import skimage.io
from PIL import Image
import cv2
import numpy as np


def img_resize(img, size=100):
    h, w, c = img.shape
    if h == w:
        img = cv2.resize(img, (size, size))
        return img
    else:
        bck = np.zeros((size, size, c), dtype=np.uint8)
        if h > w:
            w = int(w * (size/h))
            img = cv2.resize(img, (w, size))
            bck[:, int(size/2) - int(w/2) : int(size/2)+(w%2) + int(int(w/2))] = img
        else:
            h = int(h * (size/w))
            img = cv2.resize(img, (size, h))
            bck[int(size/2) - int(h/2) : int(size/2)+(h%2) + int(h/2), :] = img
        
        return bck



def img_url2b64(img_url, resize=True):
    img = skimage.io.imread(img_url)
    if resize:
        img = img_resize(img)

    img = Image.fromarray(img)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_b64


def fraction_tamer(text):
    new_text = ''
    for c in text:
        if (c.encode() == b'\xe2\x80\x89'):
            new_text += c
            continue
        try:
            name = unicodedata.name(c)
        except ValueError:
            new_text += c
            continue

        if name.startswith('VULGAR FRACTION'):
            tamed = unicodedata.normalize('NFKC', c)
            numerator, _slash, denominator = tamed.partition('⁄')
            new_text += str(numerator) + "/" + str(denominator)

        else:
            new_text += c

    return new_text


def is_ascii(c):
    return len(c.encode()) == len(c)


def ascii_forcer(text):
    new_text = ''
    for c in text:
        if is_ascii(c):
            new_text += c

    return new_text


def replace_ratios(text):
    rgx = re.compile(r'([1-9]+ )?([1-9]+/[0-9]+)')
    res = rgx.sub(
        lambda x: ratio2dec(x.group(0)), text
    )
    
    return res


def ratio2dec(ratio):
    full, partial = 0, 0
    parts = ratio.split(' ')
    if len(parts) == 1:
        partial = parts[0]
    elif len(parts) == 2:
        full = int(parts[0])
        partial = parts[1]
    else:
        raise Exception("Something sinister with {}".format(ratio))

    num, denum = [int(e) for e in partial.split('/')]
    dec = full + num / denum
    return "%.2f" % dec