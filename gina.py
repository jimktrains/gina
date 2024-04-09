#!/usr/bin/env python3

import os
import os.path
from PIL import Image,ExifTags
from jinja2 import Template
from datetime import datetime
import time
import pyexiv2

# This is a different library (I'm using https://launchpad.net/py3exiv2)
# but this has the namespace I needed and is the same issue.
# https://github.com/LeoHsiao1/pyexiv2/issues/128
pyexiv2.register_namespace('http://ns.google.com/photos/1.0/container/item/', 'Item')

src_path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(src_path, 'image.jinja') , 'r') as content_file:
    image_templ  = Template(content_file.read())
with open(os.path.join(src_path, 'index.jinja') , 'r') as content_file:
    index_templ  = Template(content_file.read())

image_links = []


class InputImage:
    def __init__(self, image):
        self.image_path = image
        self.file, self.ext = os.path.splitext(image)
        self.page_path =self.file + '.html'  
        self.thumb_size = 800
        self.thumb_path =self.file + '.thumbnail.' + str(self.thumb_size) + self.ext
        self.sm_thumb_size = 250
        self.sm_thumb_path =self.file + '.thumbnail.' + str(self.sm_thumb_size) + self.ext
        self.meta = {
            'title': self.file
        }
        metadata = pyexiv2.ImageMetadata(self.image_path)
        metadata.read()

        self.exif = metadata
        #with open(self.image_path, 'rb') as f:
        #   self.exif = EXIF.process_file(f)

        # TODO: Extracting the thumbs might be nice, but for later.

        tags_to_delete = ['Exif.Canon.CameraInfo',
                          'Exif.Photo.MakerNote', 
                          'Exif.Canon.DustRemovalData',
                          'Exif.Canon.CustomFunctions',
                          'Exif.Canon.ColorData',
                          'Exif.Canon.SensorInfo'
                          'Exif.Canon.CustomPictureStyleFileName',
                          'Exif.Canon.VignettingCorr',
                          'Exif.Canon.VignettingCorr2',
                          ]
        for tag in self.exif.keys():
            if 'Thumbnail' in tag:
                tags_to_delete.append(tag)

        for tag in tags_to_delete:
            if tag in self.exif:
                del self.exif[tag]

        if 'EXIF UserComment' in self.exif:
            if self.exif['EXIF UserComment'].printable[0] == 0:
                del self.exif['EXIF UserComment']

    def get_datetime(self):
        for tag in ['Exif.Image.DateTime']:
            if tag in self.exif:
                dt = datetime.strptime(str(self.exif[tag].raw_value), "%Y:%m:%d %H:%M:%S")
                return time.mktime(dt.timetuple())
        return os.path.getctime(self.image_path)

    def get_datetime_str(self):
        for tag in ['Exif.Image.DateTime']:
            if tag in self.exif:
                return self.exif[tag].human_value
        return ""

    def make_sm_thumb(self):
        return self._make_thumb(self.sm_thumb_size, self.sm_thumb_path)
    def make_thumb(self):
        return self._make_thumb(self.thumb_size, self.thumb_path)

    def _get_rotate(self):
        # I'm trying to figure out how this is stored, at least ones from
        # my phone don't vary it?
        orientation = 0
        #if 'Image Orientation' in self.exif:
        #    orientation = self.exif['Image Orientation']

        #print(f"Orientation: {orientation}")
        return orientation
    def _rotate(self, image):
        orientation = self._get_rotate()
        if orientation == 3:   image = image.transpose(Image.ROTATE_180)
        elif orientation == 6: image = image.transpose(Image.ROTATE_270)
        elif orientation == 8: image = image.transpose(Image.ROTATE_90)
        return image

    def _make_thumb(self, size, thumb):
        if not os.path.isfile(thumb):
            im = Image.open(self.image_path)
            im = self._rotate(im)
            im.thumbnail([size,size])
            im.save(thumb, "JPEG")
        return thumb

    def make_page(self, prev_image, next_image):
        with open(self.page_path , 'w') as content_file:
            content_file.write(image_templ.render(self.__dict__, prev_image=prev_image, next_image=next_image))

def generate_prev_next(images):
    return zip([None] + images, images, images[1:] + [None])

image_files = filter(lambda x : x.lower().endswith('.jpg'),  os.listdir("."))
image_files = filter(lambda x : 'thumbnail' not in x.lower(),  image_files)
images = list(map(lambda x : InputImage(x), image_files))
images = list(sorted(images, key=InputImage.get_datetime))
list(map(InputImage.make_thumb, images))
list(map(InputImage.make_sm_thumb, images))
list(map(lambda pcn : pcn[1].make_page(prev_image=pcn[0], next_image=pcn[2]), generate_prev_next(images)))

with open('index.html', 'w') as index_file:
    index_file.write(index_templ.render(images=images))
