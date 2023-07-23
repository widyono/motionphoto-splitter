# motionphoto-splitter

Some tools to manage photos taken on Google Pixel phones (tested with 5a).

motionphoto-splitter will isolate the motionphoto video into an .mp4 file, and also separate the individual
frames into individual .jpg files.

remove_motionphoto simply chops off the motionphoto part from the original image file, and then resizes
the resulting image such that the smaller dimension becomes 1024px, and the larger dimension is resized
appropriatey to maintain the original aspect ratio.
