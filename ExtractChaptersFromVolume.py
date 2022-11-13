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
parser.add_argument('-r', '--recursive',
                    action='store_true',
                    help='Recursively search for files. Default: False')
parser.add_argument('--debug',
                    action='store_true',
                    help='Print extra messages to the console')

args = parser.parse_args()

if args.parse and not args.index:
    raise Exception('--index needs to be passed with --parse')

ext = '.cbz'
cwd = args.dir
series_regex = r'^.+?(?= [([{]| v[0-9]+)'
vol_regex = r'(?=\(?)v[\d]+(?=\)?)'
ch_regex = r'(?:c|\s)[\d]+(?:x\d)?'
title_regex = r'\[(.*?)\]'

def log(msg):
    if args.debug:
        print(str(msg))


def cleanup(extract_path=None):
    if extract_path and extract_path.exists():
        shutil.rmtree(extract_path)

ext_folder = ext_dest = Path.cwd() / 'output' / 'extracted'
cleanup(extract_path=ext_folder)

skipped_files = 0

if args.recursive:
    file_list = [(f, r) for (r, d, files) in os.walk(cwd) for f in files]
else: 
    file_list = [(f, '.') for f in os.listdir(cwd)]

for volume_file in file_list:
    if volume_file[0].endswith(ext):
        series_name = re.search(series_regex, volume_file[0]).group(0)
        ext_dest = ext_folder / volume_file[0].rsplit('.', 1)[0]
        if not ext_dest.exists():
            Path.mkdir(ext_dest, parents=True, exist_ok=True)

        with zipfile.ZipFile(cwd / volume_file[1] / volume_file[0], 'r') as f:
            f.extractall(ext_dest)
            print(f"\nProcessing: \"{volume_file[1]}\\{volume_file[0]}\"")

        old_ch = None
        not_found_counter = 0
        for file in os.listdir(ext_dest):
            if not file.endswith(('.xml', '.bak')):  # Ignore ComicInfo and the backup that metadata-manager makes
                log(file)
                volume = re.search(vol_regex, file).group(0).lstrip(' (v0').rstrip(') ').zfill(2)
                try:
                    chapter = re.search(ch_regex, file).group(0).lstrip(' (c0').rstrip(') ')
                except AttributeError:
                    print(f"No chapters found in \"{file}\". Skipping...")
                    not_found_counter += 1
                    if not_found_counter >= 3:
                        print(f"-> There seem to be not chapters in \"{volume_file[1]}\\{volume_file[0]}\". Skipping...")
                        skipped_files += 1
                        break
                    else:
                        continue
                not_found_counter = 0
                if 'x' in chapter: chapter = chapter.zfill(5)
                else: chapter = chapter.zfill(3)

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
                output_file = f"{(cwd / 'output' / series_name / chapter_folder).resolve()}{ext}"

                if not os.path.exists(f"{(cwd / 'output' / series_name).resolve()}"): 
                    os.mkdir(f"{(cwd / 'output' / series_name).resolve()}")

                print(f'Creating: \"{chapter_folder}{ext}\"')

                with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_STORED) as archive:
                    for file_path in output_folder.rglob("*"):
                        archive.write(file_path, arcname=file_path.relative_to(output_folder))

        cleanup(ext_folder)

if skipped_files == 1:
    print("\nFinished, but 1 file was skipped. Check the console for more info.\n")
elif skipped_files > 1:
    print(f"\nFinished, but {skipped_files} files were skipped. Check the console for more info.\n")
else:
    print("\nFinished.\n")
