# photos-date-correction

Applies the shift to the file creation time in exif. In addition sets this value as the file modification date. Saves the new file with the modified timestamp in the "output" folder. 

The following parameters can be used:

-p <path> : path to the folder with photos

-x <prefix> : a prefix to add to output files in necessary

-s <shift_in_min> : a time shift to apply to the photo timestamp, in minutes

-t <filter> : a filter to process only with certain files
