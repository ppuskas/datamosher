#!/usr/bin/env python3

import argparse
import subprocess
import os
import json


def get_vectors(input_video):
    # extract video data using ffedit
    subprocess.call(f'ffedit -i {input_video} -f mv:0 -e tmp.json', shell=True)

    # read the data we extracted
    f = open('tmp.json', 'r')
    raw_data = json.load(f)
    f.close()
    os.remove('tmp.json')

    # read frame information
    frames = raw_data['streams'][0]['frames']

    # get vectors from each frame
    vectors = []
    for frame in frames:
        try:
            vectors.append(frame['mv']['forward'])
        except:
            vectors.append([])

    return vectors


def apply_vectors(vectors, input_video, output_video, method='add'):
    subprocess.call(f'ffgac -i {input_video} -an -mpv_flags +nopimb+forcemv -qscale:v 0 -g {gop_period}' +
                    ' -vcodec mpeg2video -f rawvideo -y tmp.mpg', shell=True)

    # open js file and read its contents
    to_add = '+' if method == 'add' else ''
    script_contents = '''
    var vectors = [];
    var n_frames = 0;

    function glitch_frame(frame) {
        let fwd_mvs = frame["mv"]["forward"];
        if (!fwd_mvs || !vectors[n_frames]) {
            n_frames++;
            return;
        }

        for ( let i = 0; i < fwd_mvs.length; i++ ) {
            let row = fwd_mvs[i];
            for ( let j = 0; j < row.length; j++ ) {
                let mv = row[j];
                try {
                    mv[0] ''' + to_add + '''= vectors[n_frames][i][j][0];
                    mv[1] ''' + to_add + '''= vectors[n_frames][i][j][1];
                } catch {}
            }
        }

        n_frames++;
    }
    '''

    script_path = 'apply_vectors.js'

    # open js file and write the code
    with open(script_path, 'w') as f:
        f.write(script_contents.replace('var vectors = [];', f'var vectors = {json.dumps(vectors)};'))

    # apply the effect
    subprocess.call(f'ffedit -i tmp.mpg -f mv -s {script_path} -o {output_video}', shell=True)

    # remove temp files
    os.remove('apply_vectors.js')
    os.remove('tmp.mpg')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', type=str, default=1000, dest='gop_period', help='I-frame period (in frames)')
    parser.add_argument('-v', type=str, default='', dest='vector_file',
                        help='file containing vector data to transfer', required=False)
    parser.add_argument('-e', type=str, default='', dest='extract_from',
                        help='video to extract motion vector data from', required=False)
    parser.add_argument('-t', default='', type=str, dest='transfer_to', help='video to transfer motion vector data to')
    parser.add_argument(default='', type=str, dest='output',
                        help='output file either for the final video, or for the vector data')
    return parser.parse_args().__dict__


if __name__ == '__main__':
    # get args
    args = parse_args()
    gop_period = args['gop_period']
    vector_file = args['vector_file']
    extract_from = args['extract_from']
    transfer_to = args['transfer_to']
    output = args['output']

    # check that either extract_from or vector_file is given
    if not ((extract_from == '') ^ (vector_file == '')):
        print('Only one of -v or -e must be given')
        exit(0)

    vectors = []

    if extract_from:
        # step 1a: extract vectors
        subprocess.call(f'ffgac -i {extract_from} -an -mpv_flags +nopimb+forcemv -qscale:v 0 -g {gop_period}' +
                        ' -vcodec mpeg2video -f rawvideo -y tmp.mpg', shell=True)
        vectors = get_vectors('tmp.mpg')
        os.remove('tmp.mpg')

        # if we only have to extract the vectors, write to file and exit
        if transfer_to == '':
            with open(output, 'w') as f:
                json.dump(vectors, f)
            exit(0)
    elif vector_file:
        # step 1b: read vectors from file
        if not transfer_to:
            print('Please specify file to transfer vectors to using -t')
            exit(0)

        with open(vector_file, 'r') as f:
            vectors = json.load(f)

    # step 2: transfer vector data to file
    apply_vectors(vectors, transfer_to, output)
