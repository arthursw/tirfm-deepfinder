import shlex
import shutil
import argparse
from pathlib import Path
import subprocess
from deepfinder.commands.convert_tiff_to_h5 import convert_tiff_to_h5

def detect_spots(tiffs_path, detector_path, command, output_path):
    output_folder = output_path.with_suffix('')
    output_folder.mkdir(exist_ok=True, parents=True)
    command = command.replace('{detector}', str(detector_path.resolve()))
    command = command.replace('{input}', str(tiffs_path.resolve()))
    command = command.replace('{output}', str(output_folder.resolve()))
    subprocess.run(shlex.split(command))
    
    convert_tiff_to_h5(output_folder, output_path, make_subfolder=False)
    shutil.rmtree(output_folder)
    return

def main():
    parser = argparse.ArgumentParser('Detect spots', description='Detect spots and convert resulting segmentation to h5.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-m', '--movie', help='Path to the input folder containing one tiff file per frame.', default='tiff/', type=Path)
    parser.add_argument('-dp', '--detector_path', help='Path to the detector.', default='path/to/atlas', type=Path)
    parser.add_argument('-dc', '--detector_command', help='Command to detect spots. {detector} will be replaced by the --detector_path argument. {input} will be replaced by the input frame, {output} by the output frame.', default='python "{detector}/compute_segmentations.py" --atlas "{detector}/build/" --dataset "{input}" --output "{output}"', type=str)
    parser.add_argument('-o', '--output', help='Path to the output segmentations.', default='detector_segmentation.h5', type=Path)
    parser.add_argument('-b', '--batch', help='Path to the root folder containing all folders to process. If given, all other path arguments must be relative to the folders to process.', default=None, type=Path)

    args = parser.parse_args()

    movie_paths = sorted([d for d in args.batch.iterdir() if d.is_dir()]) if args.batch is not None else [args.movie]

    for movie_path in movie_paths:
        print('Process', movie_path)
        tiff_path = movie_path / args.movie if args.batch is not None else args.movie
        output_path = movie_path / args.output if args.batch is not None else args.output
        detect_spots(tiff_path, args.detector_path, args.detector_command, output_path)

if __name__ == '__main__':
    main()