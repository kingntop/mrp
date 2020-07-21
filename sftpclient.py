import paramiko
import datetime, os
import glob
from sftpconn import sftpconn
import shutil
import json


now = datetime.datetime.now() - datetime.timedelta(minutes=10)
YMD = now.strftime("%Y%m%d")
HMD = now.strftime("%Y%M")
YMD = '20200620'

JSON_BASE = '/home/mrp/Script/'

PLOG = '/home/mrp/Script/paramiko.log'

LOCAL  = '/home/mrp/Script/logs/'
REMOTE = '/logs/uplus'
DIRS  = ['/arentService11/tloLog/', '/arentService12/tloLog/']

def set_Env():
    with open(JSON_BASE + "mrp/env.json") as json_file:
        json_data = json.load(json_file)
        global HOSTS, USERNAME, PASSWORD
        HOSTS = json_data["server"]
        USERNAME = json_data["id"]
        PASSWORD = json_data["pwd"]
        print (HOSTS)

def check_dir(PATH):
    try:
        os.makedirs(PATH)
    except OSError:
        pass

def remove_dir(PATH):
    try:
        os.makedirs(LOCAL + YMD)
    except OSError:
        pass

def remove_basefile(PATH):
    fileList = glob.glob(PATH + '*.log')
    # shutil.rmtree(PATH)
    print('remove_basefile_filelist', fileList)
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)

def concatFiles(PATH, filename):
    file_list = glob.glob(PATH+'*.log')
    with open(PATH + filename, 'a') as merge_file :
        print ('concate file lsit ', file_list)
        for fname in file_list:
            with open(fname, 'r') as f:
                for line in f:
                    merge_file.write(line)
    

def localfile_list (PATH):
    arr = os.listdir(PATH)
    print('file', arr)  
    return arr


if __name__ == "__main__":
    set_Env()
    local_base = LOCAL + YMD + '/';
    remove_basefile(local_base);
    for host in HOSTS :
        try :
            f = sftpconn(PLOG, USERNAME, PASSWORD, host, '22', False);
            for servicenum in DIRS :
                local_host = local_base + '/' + host + '/'
                check_dir(local_host)
                print(local_host)
                lfiles = localfile_list(local_host)
                f.get(lfiles, local_host, local_base, REMOTE + servicenum + YMD + '/')
            f.close()
        except Exception as e:
            print(e)

    concatFiles(local_base, YMD + HMD + '.txt')