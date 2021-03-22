Datamoshing made easy. 

## Requirements
`mosh.py` requires `ffmpeg` to be installed.
`vector_motion.py` and `style_transfer.py` rely on `ffedit` and `ffgac`, which can be downloaded from [ffglitch.org](https://ffglitch.org/)

# Effects

## I frame removal
This type of glitch creates the transition effect. Example:

`python mosh.py input.mp4 -s 40 -e 90 -o output.mp4` removes all the i-frames from the input video starting at frame 40 and ending at frame 90, and outputs the final result to `output.mp4`

## Delta frame duplication
Repeats a series of p-frames (aka delta frames), which can give a 'melting' effect. This type of glitch is triggered by the `-d` flag. Example:

`python mosh.py input.mp4 -d 30 -s 30 -e 120 -o output.mp4` copies frames with indexes [30, 59] and overwrites frames [60, 89] and [90, 119] with the copied data.

## Vector motion
While the previous effects copy and delete whole frames, this one changes the actual frame data. As explained in [this article on ffglitch.org](https://ffglitch.org/2020/07/mv.html), you need to write a custom JavaScript file that can change the frame data. `vector_motion.py` is just a wrapper for `ffedit` and `ffgac`.
Example:

`python vector_motion.py input.mp4 -s your_script.js -o output.mp4`

I am planning to add support for moshing using python scripts in the near future (but this will be done internally through a js script).

## Style transfer
I call style transfer combining the motion vectors of two videos together (by simply adding them together). For example, applying the vector motion data of a person talking to a video of clouds can make it look as though the clouds are talking. 
This script can also extract motion vector data from a video and write it to a file, or read motion data from file and apply it to a video.

Examples:

`python style_transfer.py -e person_talking.mp4 -t clouds.mp4 -o output.mp4` copies vector data from `person_talking.mp4`, transfers it to `clouds.mp4` and outputs the video to `output.mp4`.

`python style_transfer.py -e person_talking.mp4 -o vectors.json` gets the vector data from `person_talking.mp4` and outputs it to `vectors.json`.

`python style_transfer.py -v vectors.json -t clouds.mp4 -o output.mp4` loads vector data from `vectors.json`, transfers it to `clouds.mp4` and outputs the video to `output.mp4`.
