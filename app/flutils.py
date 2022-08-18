#-*- coding: UTF-8 -*- 

import logging, inspect
import datetime
import shutil
import os, glob
#import pandas as pd


def check_dir_writable(dnm):
    return os.access(dnm, os.W_OK)


def check_file_writable(fnm):  
    
    if os.path.exists(fnm):
        # path exists
        if os.path.isfile(fnm): # is it a file or a dir?
            # also works when file is a link and the target is writable
            return os.access(fnm, os.W_OK)
        else:
            return False # path is a dir, so cannot write as a file
    # target does not exist, check perms on parent dir
    pdir = os.path.dirname(fnm)
    if not pdir: pdir = '.'
    # target is creatable if parent dir is writable
    return os.access(pdir, os.W_OK)


def moveFile(fnm, dnm, action='move'):
    #logging.info(' Inside moveFile: filename {0} directory name {1} at {2}'.format(fnm,dnm,datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    #write_log('moveFile filename {0} directory name {1}'.format(fnm,dnm))
    dir_writeable = check_dir_writable(dnm)

    if dir_writeable == True:
        for file in glob.glob(fnm):
            try:
                if action == 'move':
                    shutil.move(file, dnm)
                    #logging.info(' File {0} moved to directory {1} at {2}'.format(file,dnm,datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
                    write_log('File {0} moved to directory {1}'.format(file,dnm))
                    result = True
                elif action == 'copy':
                    shutil.copy(file, dnm)
                    #logging.info(' File {0} copied to directory {1} at {2}'.format(file,dnm,datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
                    write_log('File {0} copied to directory {1}'.format(file,dnm))
                    result = True
                else:
                    write_log('Action {} was incorrect'.format(action))
                    result = False
            except Exception as e:
                #logging.info(' File couldn\'t be moved to directory. Error was ' + str(e))
                write_log('File couldn\'t be moved to directory. Error was ' + str(e))
                result = False    
            return result
    else:
        #logging.error(' File {0} couldn\'t be moved to directory {1} at {2} '.format(file,dnm,datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))    
        write_log('File {0} couldn\'t be moved to directory {1}'.format(fnm,dnm))
        return False

    
def setupLogging(logs_dir,prefix=''):
    
    logfile = logs_dir + prefix + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + ".log"
    logger = logging
    logger.basicConfig(filename=logfile,level=logging.INFO)
    logger.info('-' * 80)
    logger.info(inspect.stack()[0][3] + ' Logging started at ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    logger.info('-' * 80)
    return logfile

def write_log(log_message): #TODO: Add DEBUG, INFO support    
    logging.info(inspect.stack()[1][3] + ' ' + log_message + ' at ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    
    
    
def write_csv_data(df, fname, download_dir):
    
    run_date = datetime.datetime.today()
    ldate = (run_date).strftime('%Y%m%d')    # ldate = logfile date
    
    fname = download_dir + fname + "_" + str(ldate) + ".csv"
    write_log('Writing csv file {0} with GPS data updates'.format(fname))
    df.to_csv(fname)
    return True