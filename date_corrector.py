from datetime import timedelta, datetime
import time
import sys
import os
import glob
from PIL import Image
import piexif
import argparse

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")


class DateCorrector:
    """
    Corresponds to a folder with photos coming from the same camera.
    """

    def __init__(self, path, prefix, time_shift_minutes):
        self.path = path
        self.prefix = prefix
        self.time_shift = time_shift_minutes
        self.fileNameTemplate = '*'

    def set_name_template(self, template):
        """
        Sets the file name template.
        """
        self.fileNameTemplate = template

    def _read_file_list(self):
        files = list()
        if os.path.exists(self.path):
            files = glob.glob(os.path.join(self.path, '**', self.fileNameTemplate), recursive=True)
        return files

    def _fix_file_timestamp(self, file_path):
        """
        Reads a timestamp from one file's EFIF data, applies the shift if it's set and creates a new file with a fixed
        timestamp in a folder "output" created in the original folder.
        """
        with Image.open(file_path) as image:
            print("Fixing " + file_path)
            tags = piexif.load(image.info["exif"])
            # other keys : '0th', 'Exif', 'GPS', 'Interop', '1st', 'thumbnail'
            # the key for the original time           
            key = piexif.ExifIFD.DateTimeOriginal
            # print(tags['Exif'][key])
            if ('Exif' in tags.keys()) and (key in tags['Exif'].keys()):
                # fix the original time
                timestamp_fixed = datetime.strptime(str(tags['Exif'][key]), 'b\'%Y:%m:%d %H:%M:%S\'') + self.time_shift
                tags['Exif'][key] = timestamp_fixed.strftime('%Y:%m:%d %H:%M:%S')  # works, surprisingly
                # print(tags['Exif'][key])
                # fix the digitized time
                key = piexif.ExifIFD.DateTimeDigitized
                # print(tags['Exif'][key])
                timestamp_fixed = datetime.strptime(str(tags['Exif'][key]), 'b\'%Y:%m:%d %H:%M:%S\'') + self.time_shift
                tags['Exif'][key] = timestamp_fixed.strftime('%Y:%m:%d %H:%M:%S')
                # print(tags['Exif'][key])

                # write results
                dir_name = os.path.join(os.path.dirname(file_path), "output")
                os.makedirs(dir_name, exist_ok=True)
                file_name = os.path.basename(file_path)
                new_file_path = os.path.join(dir_name, self.prefix + file_name)
                exif_bytes = piexif.dump(tags)
                image.save(new_file_path, "JPEG", quality=100, exif=exif_bytes)

                # set the file modification time 
                modification_time = time.mktime(timestamp_fixed.timetuple())
                os.utime(new_file_path, (modification_time, modification_time))
            else:
                print("Corrupted " + file_path)

    def fix_files(self):
        files = self._read_file_list()
        if files:
            for file_path in files:
                self._fix_file_timestamp(file_path)
            print('Finished, {0} files were processed'.format(len(files)))
        else:
            print('Nothing to fix in' + self.path)


if __name__ == '__main__':
    # The files with corrected timestamp will be copied in a new folder called "output" in the original path to photos.
    # TODO: consider providing a destination path.
    parser = argparse.ArgumentParser(description='Correct the date of photos.')
    parser.add_argument('-p', '--path', type=str, help='Path to the folder', required=True)
    parser.add_argument('-x', '--prefix', type=str, help='Prefix to add', required=True)
    parser.add_argument('-s', '--shift', type=int, help='Time shift in minutes to apply', required=True)
    parser.add_argument('-t', '--template', type=str, help='Template of image names', required=True)
    args = parser.parse_args()

    shift = args.shift
    source = DateCorrector(args.path, args.prefix, timedelta(minutes=shift))
    source.set_name_template(args.template)
    source.fix_files()

