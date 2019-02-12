import requests

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile


def ImageFileFromUrl(url):
    r = requests.get(url)
    r.raise_for_status()

    img_temp = NamedTemporaryFile()
    img_temp.write(r.content)
    img_temp.flush()

    return File(img_temp)