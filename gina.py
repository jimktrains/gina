#!/usr/bin/evn python3

import os
from PIL import Image
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
        self.thumb_size = 640
        self.thumb_path =self.file + '.thumbnail.' + str(self.thumb_size) + self.ext
        self.sm_thumb_size = 150
        self.sm_thumb_path =self.file + '.thumbnail.' + str(self.sm_thumb_size) + self.ext
        self.meta = {
            'title': self.file
        }
    def make_sm_thumb(self):
        return self._make_thumb(self.sm_thumb_size, self.sm_thumb_path)
    def make_thumb(self):
        return self._make_thumb(self.thumb_size, self.thumb_path)

    def _make_thumb(self, size, thumb):
        if not os.path.isfile(thumb):
            im = Image.open(self.image_path)
            im.thumbnail([size,size])
            im.save(thumb, "JPEG")
        return thumb

    def make_page(self):
        thumb = self.make_thumb()
        
        with open(self.page_path , 'w') as content_file:
            content_file.write(image_templ.render(self.__dict__))

image_files = filter(lambda x : x.lower().endswith('.jpg'),  os.listdir("."))
image_files = filter(lambda x : 'thumbnail' not in x.lower(),  image_files)
images = list(map(lambda x : InputImage(x), image_files))
list(map(InputImage.make_thumb, images))
list(map(InputImage.make_sm_thumb, images))
list(map(InputImage.make_page, images))

with open('index.html', 'w') as index_file:
    index_file.write(index_templ.render(images=images))
