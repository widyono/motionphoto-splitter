#!/usr/bin/env python3

"""
motionphoto_splitter.py

Google Pixel Motion Photo splitter. Works with modern Pixel Motion Photos which embed
MP4 length in EXIF header (filenames should look like PXL_*.MP.jpg). This will not work
with older format MVIMG_*.jpg files! (yet...). Tested with Android 12 phone data.

Input: blah.MP4.jpg combined JPG and MP4 container
Output: blah.MP_detached.jpg JPG
        blah.MP_detached.mp4 MP4 video
        blah.MP_frame####.jpg individual video frames as JPG

Combination of code / ideas from:
https://github.com/ViRb3/google-camera-motion-photo-splitter/blob/master/splitter.py
https://www.codegrepper.com/code-examples/python/split+mp4+into+frames+python
https://www.file-recovery.com/mp4-signature-format.htm
https://github.com/nextcloud/photos/issues/365#issuecomment-982014436
"""

from sys import argv
from os import path, mkdir
from mmap import mmap, ACCESS_READ
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, imwrite
from math import ceil, log

for filename in argv[1:]:
    try:
        with open(filename,'rb') as f_in:
            base_pathname = filename.replace('.jpg','')
            picture_filename = base_pathname + "_detached_topshot.jpg"
            video_filename = base_pathname + "_detached_frames.mp4"
            frames_directory = base_pathname + "_frames/"
            _, base_filename = path.split(base_pathname)
            frames_filename_prefix = frames_directory + base_filename + "_frame" # ... + zero padded index + ".jpg"

            mm = mmap(f_in.fileno(),0,access=ACCESS_READ)
            file_size = mm.size()
            motionphoto_headeroffset = mm.find(b'Item:Semantic="MotionPhoto"')
            motionphoto_lengthoffset = mm.find(b'Item:Length="',motionphoto_headeroffset)
            motionphoto_lengthending = mm.find(b'"',motionphoto_lengthoffset+13)
            mm.seek(motionphoto_lengthoffset + 13)
            motionphoto_length = int(mm.read(motionphoto_lengthending - motionphoto_lengthoffset - 13))
            motionphoto_datastart = file_size - motionphoto_length
            mm.seek(0)
            with open(picture_filename,'wb') as f_out:
                f_out.write(mm.read(motionphoto_datastart))
            with open(video_filename,'wb') as f_out:
                f_out.write(mm.read())
            mkdir(frames_directory)
            vidcap = VideoCapture(video_filename)
            numframes = vidcap.get(CAP_PROP_FRAME_COUNT)
            framenum_maxwidth = ceil(log(numframes,10))
            framecount = 0
            success,image = vidcap.read()
            while success:
                imwrite(f"{frames_filename_prefix}{framecount:0{framenum_maxwidth}}.jpg", image)
                success,image = vidcap.read()
                framecount += 1
            mm.close()
    except (OSError,) as err:
        print(f"Problem splitting {filename}: {err}.")
        continue
