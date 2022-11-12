from pathlib import Path
import argparse
import zipfile
import shutil
import os
import re


parser = argparse.ArgumentParser(description='')
parser.add_argument('-p', '--parse',
                    action='store_true',
                    help='Parse the title from the filename. Default: False')
parser.add_argument('-i', '--index',
                    type=int,
                    default=2,
                    help="Position in filename for the title. Found with filename.split('['). Default: 2")
parser.add_argument('-d', '--dir',
                    default=Path.cwd(),
                    help='Location to run the script on. Default: Current directory')
parser.add_argument('--debug',
                    action='store_true',
                    help='Print extra messages to the console')

args = parser.parse_args()

if args.parse and not args.index:
    raise Exception('--index needs to be passed with --parse')

ext = '.cbz'
cwd = args.dir
vol_regex = r'(?:v)[\d)]+'
ch_regex = r'c([^\s]+)'
title_regex = r'\[(.*?)\]'

def log(msg):
    if args.debug:
        print(str(msg))


def cleanup(extract_path=None):
    if extract_path and extract_path.exists():
        shutil.rmtree(extract_path)


ext_folder = ext_dest = Path.cwd() / 'output' / 'extracted'
cleanup(extract_path=ext_folder)

for volume_file in os.listdir(cwd):
    if volume_file.endswith(ext):
        ext_dest = ext_folder / volume_file.rsplit('.', 1)[0]
        if not ext_dest.exists():
            Path.mkdir(ext_dest, parents=True, exist_ok=True)

        with zipfile.ZipFile(cwd / volume_file, 'r') as f:
            f.extractall(ext_dest)
            print(f"Processing: {volume_file}")

        old_ch = None
        for file in os.listdir(ext_dest):
            if not file.endswith(('.xml', '.bak')):  # Ignore ComicInfo and the backup that metadata-manager makes
                log(file)
                volume = re.search(vol_regex, file).group(0).lstrip('v').rstrip(')').lstrip('0').zfill(2)
                chapter = re.search(ch_regex, file).group(0).lstrip('c').lstrip('0').zfill(3)

                if args.parse:
                    try:
                        if old_ch != chapter:  # Only parse once per chapter
                            possible_titles = re.findall(title_regex, file)
                            title = possible_titles[args.index]
                            print(f'Vol. {volume} Ch. {chapter} title parsed as: {title}')
                        old_ch = chapter
                    except IndexError:
                        raise Exception("Your index is too high or too low! Double check your filenames and try again")
                    new_folder = f"Vol. {volume} Ch. {chapter} - {title}"
                else:
                    new_folder = f"Vol. {volume} Ch. {chapter}"

                Path.mkdir(ext_dest / new_folder, exist_ok=True)
                shutil.move((ext_dest / file), (ext_dest / new_folder / file))

        # Save the new files
        for root, dirs, files in os.walk(ext_dest):
            for chapter_folder in dirs:

                output_folder = (ext_dest / chapter_folder).resolve()
                output_file = f"{(cwd / 'output' / chapter_folder).resolve()}{ext}"

                print(f'Creating: {chapter_folder}{ext}')

                with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_STORED) as archive:
                    for file_path in output_folder.rglob("*"):
                        archive.write(file_path, arcname=file_path.relative_to(output_folder))

        cleanup(ext_folder)

print("Done")
