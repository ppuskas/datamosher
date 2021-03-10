#!/usr/bin/env python3

import argparse
import subprocess
import os

parser = argparse.ArgumentParser()
parser.add_argument('input_video', type=str, help='specifies input file')
parser.add_argument('-s', type=str, dest='script_path', help='path to the js script', required=True)
parser.add_argument('-g', type=str, default=300, dest='gop_period', help='I-frame period (in frames)')
parser.add_argument('-o', default='moshed.mpg', type=str, dest='output_video', help='output file for the moshed video')
args = parser.parse_args().__dict__

input_video = args['input_video']
gop_period = args['gop_period']
output_video = args['output_video']
script_path = args['script_path']

subprocess.call(f'ffgac -i {input_video} -an -mpv_flags +nopimb+forcemv -qscale:v 0 -g {gop_period}' +
                ' -vcodec mpeg2video -f rawvideo -y tmp.mpg', shell=True)

subprocess.call(f'ffedit -i tmp.mpg -f mv -s {script_path} -o {output_video}', shell=True)

os.remove('tmp.mpg')
