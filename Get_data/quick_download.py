import numpy as np
from subprocess import call
import urllib
import sys
import os.path


def dlProgress(count, blockSize, totalSize):
    percent = float(count)*blockSize*100.0/totalSize
    sys.stdout.write("\r...%6.2f%%" % percent)
    sys.stdout.flush()


def go():
    url_dir = 'https://nyctaxitrips.blob.core.windows.net/data/' 
    nfiles = 12
    dat_filenames = \
        [('trip_data_'+str(i)+'.csv.zip') for i in range(1,nfiles+1)]
    fare_filenames = \
        [('trip_fare_'+str(i)+'.csv.zip') for i in range(1,nfiles+1)]

##    print dat_filenames
    
    for df, ff in zip(dat_filenames, fare_filenames):
        testfile = urllib.URLopener()
        
        if not os.path.isfile(df):
            print df
            print url_dir+df
            testfile.retrieve(url_dir+df, df, reporthook = dlProgress)
            print ""

        if not os.path.isfile(ff):
            print url_dir + ff
            testfile.retrieve(url_dir+ff, ff, reporthook = dlProgress)
            print ""



#         command = "wget '" + df + "'"
#         print command
#         call(command)

#         command = 'wget ' + ff
#         print command
#         call(command)



