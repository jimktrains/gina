gina
====

Generates static image galleries

Take a simple folder, `pics`,  containing

* pics/IMG_2012.JPG
* pics/IMG_2012.meta

Where `pics/IMG_2012.JPG` is a jpeg and `pics/IMG_2012.meta` is a key-value pair file where each pair is represented according to [HTTP Header (REFC 2616 &sect; 14)](http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html format):

    Key1: Value
    Key2: Value
    ...

Some keys that are/will be recognize:

* Title: (string)
* Event: (string)
* Tags: (comma separated strings)
* Date: iso-8601 string
* Geo: lat,lon
* License: (string name), (string url) # Note: I will auto-recognize certain ones like CC-SA, CC-A, CC-NC and such
* Source: (string telling where the image is located if not in the same directory. Useful for storing images on S3.)

Additionally, there needs to be a `properties.yml` (similar to [gus](https://github.com/jimktrains/gus)) file in the root dir describing how to create the static indexes, sizes to resize to, templates, &c
