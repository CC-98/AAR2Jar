from genericpath import exists
import os
import re
import subprocess as sp
from glob import glob
import shutil
import zipfile


searchStr = "#"
# P_isDebug = "Debug"
P_isDebug = "Release"
# P_filename_isdebug = 'debug'
P_filename_isdebug = 'release'
P_curposition = os.getcwd()
P_resFilePosition = P_curposition+"/res/build.gradle"
P_replaceFileContent = P_curposition+"/jar_name.ini"
P_targetFilePosition = P_curposition+"/app/build.gradle"
P_resourse_jar = P_curposition+"/app/build/dependencies/"+P_filename_isdebug
P_target_jar = P_curposition+"/sdk"
P_target_jar_inner = P_curposition+"/sdk/"
P_target_zip = P_curposition+"/sdk.zip"

P_Gradle_Store_Root = 'C:/Users/dujinshan/.gradle/caches/modules-2/files-2.1'

P_FileToStoreDepend = P_curposition+"/dependSave.txt"
P_FileTmp = P_curposition+"/Tmp.txt"





# 如果存在上一次运行的结果，首先要进行清除
def F_clear_last_run():
    if os.path.isfile(P_target_zip):
        os.remove(P_target_zip)
    if os.path.isdir(P_target_jar):
        shutil.rmtree(P_target_jar)
    if os.path.isdir(P_resourse_jar):
        shutil.rmtree(P_resourse_jar)



F_clear_last_run()