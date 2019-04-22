#!/usr/bin/env python3

import os
from PIL import Image,ExifTags
from jinja2 import Template


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
    def make_sm_thumb(self):
        return self._make_thumb(self.sm_thumb_size, self.sm_thumb_path)
    def make_thumb(self):
        return self._make_thumb(self.thumb_size, self.thumb_path)

    def _get_rotate(self, image):
        if hasattr(image, '_getexif'): # only present in JPEGs
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            e = image._getexif()       # returns None if no EXIF data
            if e is not None:
                exif=dict(e.items())
                if orientation in exif:
                    orientation = exif[orientation]

            return orientation
    def _rotate(self, image):
        orientation = self._get_rotate(image)
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
        thumb = self.make_thumb()
        
        with open(self.page_path , 'w') as content_file:
            content_file.write(image_templ.render(self.__dict__, prev_image=prev_image, next_image=next_image))

def generate_prev_next(images):
    return zip([None] + images, images, images[1:] + [None])

image_files = filter(lambda x : x.lower().endswith('.jpg'),  os.listdir("."))
image_files = filter(lambda x : 'thumbnail' not in x.lower(),  image_files)
images = list(map(lambda x : InputImage(x), image_files))
list(map(InputImage.make_thumb, images))
list(map(InputImage.make_sm_thumb, images))
list(map(lambda pcn : pcn[1].make_page(prev_image=pcn[0], next_image=pcn[2]), generate_prev_next(images)))

with open('index.html', 'w') as index_file:
    index_file.write(index_templ.render(images=images))
