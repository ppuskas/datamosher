import os
import argparse
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument('input_video', type=str, help='File to be moshed')
parser.add_argument('--output_width', default=1920, type=int, help='Width of output video in pixels.')
parser.add_argument('--start_frame', '-s', default=0, type=int, help='start frame of the mosh')
parser.add_argument('--end_frame', '-e', default=-1, type=int, help='end frame of the mosh')
parser.add_argument('--fps', '-f', default=30, type=int, help='fps to convert initial video to')
parser.add_argument('--delta', '-d', action='store_true')
args = parser.parse_args().__dict__

input_video = args['input_video']
output_width = args['output_width']
start_frame = args['start_frame']
end_frame = args['end_frame']
fps = args['fps']
delta = args['delta']

file_name = os.path.splitext(os.path.basename(input_video))[0]
input_avi = 'datamoshing_input.avi'  # must be an AVI so i-frames can be located in binary file
output_avi = 'datamoshing_output.avi'
output_video = f'{file_name}_moshed.mp4'

# convert original file to avi
subprocess.call('ffmpeg -loglevel error -y -i ' + input_video + ' ' +
                ' -crf 0 -pix_fmt yuv420p -bf 0 -b 4096k -r ' + str(fps) + ' ' +
                # ' -ss ' + str(start_sec) + ' -to ' + str(end_sec) + ' ' +
                input_avi, shell=True)

# open up the new files so we can read and write bytes to them
in_file = open(input_avi, 'rb')
out_file = open(output_avi, 'wb')

# because we used 'rb' above when the file is read the output is in byte format instead of Unicode strings
in_file_bytes = in_file.read()

# 0x30306463 which is ASCII 00dc signals the end of a frame.
frame_end = bytes.fromhex('30306463')

# get all frames of video
frames = in_file_bytes.split(frame_end)

# 0x0001B0 signals the beginning of an i-frame. Additional info: 0x0001B6 signals a p-frame
iframe = bytes.fromhex('0001B0')


def mosh_iframe_removal():
    for index, frame in enumerate(frames):
        if index < start_frame or 0 < end_frame < index or frame[5:8] != iframe:
            out_file.write(frame + frame_end)


def mosh_delta_repeat():
    to_repeat = b''
    for index, frame in enumerate(frames):
        if index < start_frame or 0 < end_frame < index:
            out_file.write(frame + frame_end)
        elif index > start_frame and (end_frame < 0 or index < end_frame):
            if to_repeat == b'' and frame[5:8] != iframe:
                to_repeat = frame
            elif to_repeat != b'':
                out_file.write(to_repeat + frame_end)
            else:
                out_file.write(frame + frame_end)


if delta:
    mosh_delta_repeat()
else:
    mosh_iframe_removal()

in_file.close()
out_file.close()

# export the video
subprocess.call('ffmpeg -loglevel error -y -i ' + output_avi + ' ' +
                ' -crf 18 -pix_fmt yuv420p -vcodec libx264 -acodec aac -r ' + str(fps) + ' ' +
                ' -vf "scale=' + str(output_width) + ':-2:flags=lanczos" ' + ' ' +
                # ' -ss ' + str(start_sec) + ' -to ' + str(end_sec) + ' ' +
                output_video, shell=True)

# gets rid of the in-between files so they're not crudding up your system
os.remove(input_avi)
os.remove(output_avi)
