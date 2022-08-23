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


# 入口函数
def F_init():
    F_clear_last_run()
    F_replace_target_file()
    F_powershell_run(F_writeDown_dependsName)
    F_CopyFileFromGradleRoot()
    return

# 调用gradlew命令后要执行的内容
def copy_file_and_zip():
    shutil.copytree(P_resourse_jar,P_target_jar)
    F_zip_jarclass(P_target_jar,P_target_zip)
    return 

# 如果存在上一次运行的结果，首先要进行清除
def F_clear_last_run():
    if os.path.isfile(P_target_zip):
        os.remove(P_target_zip)
    if os.path.isdir(P_target_jar):
        shutil.rmtree(P_target_jar)
    if os.path.isdir(P_resourse_jar):
        shutil.rmtree(P_resourse_jar)

# 压缩存放jar的文件夹
def F_zip_jarclass(dirpath,outfullname):
    if os.path.exists(outfullname):
        os.remove(outfullname) # 判断存在的话就删除
    if os.path.exists(os.path.join(dirpath,os.path.split(outfullname)[-1])):
        os.remove(os.path.join(dirpath,os.path.split(outfullname)[-1]))
    zip = zipfile.ZipFile(outfullname,"a",zipfile.ZIP_DEFLATED)
    for file in os.listdir(dirpath):
        zip.write(os.path.join(dirpath,file),file) # 解决压缩目录嵌套问题
    zip.close()
    # shutil.move(dirpath,outfullname) # 移动文件

# 获取文件内容
def F_getFileContent(posiotion):
    FL_curF = open(posiotion,"r+")
    P_curF_content = FL_curF.read()
    FL_curF.close()
    return P_curF_content
# 用对应内容替换模板内容
def F_replace_jar_name():
    FL_temp_content = F_getFileContent(P_resFilePosition)
    FL_replace_str = F_getFileContent(P_replaceFileContent)
    FL_temp_content = re.sub(searchStr,FL_replace_str,FL_temp_content)
    return FL_temp_content
# 将替换好的内容写入对应文件
def F_replace_target_file():
    FL_target_file = open(P_targetFilePosition,"w")
    FL_target_file.write(F_replace_jar_name())
    FL_target_file.close()
# 创建powershell类来执行对应的命令
class PowerShell:
    # from scapy
    def __init__(self, coding, ):
        cmd = [self._where('PowerShell.exe'),
               "-NoLogo", "-NonInteractive",  # Do not print headers
               "-Command", "-"]  # Listen commands from stdin
        startupinfo = sp.STARTUPINFO()
        startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
        self.popen = sp.Popen(cmd, stdout=sp.PIPE, stdin=sp.PIPE, stderr=sp.STDOUT, startupinfo=startupinfo)
        self.coding = coding

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        self.popen.kill()

    def run(self, cmd, timeout=15):
        b_cmd = cmd.encode(encoding=self.coding)
        try:
            b_outs, errs = self.popen.communicate(b_cmd, timeout=timeout)
        except sp.TimeoutExpired:
            self.popen.kill()
            b_outs, errs = self.popen.communicate()
        outs = b_outs.decode(encoding=self.coding)
        return outs, errs

    @staticmethod
    def _where(filename, dirs=None, env="PATH"):
        """Find file in current dir, in deep_lookup cache or in system path"""
        if dirs is None:
            dirs = []
        if not isinstance(dirs, list):
            dirs = [dirs]
        if glob(filename):
            return filename
        paths = [os.curdir] + os.environ[env].split(os.path.pathsep) + dirs
        try:
            return next(os.path.normpath(match)
                        for path in paths
                        for match in glob(os.path.join(path, filename))
                        if match)
        except (StopIteration, RuntimeError):
            raise IOError("File not found: %s" % filename)

# 执行命令创建对应jar包
def F_powershell_run(callback_fun):
    with PowerShell('GBK') as ps:
        # outs, errs = ps.run('./gradlew copyDependenciesDebug')
        outs, errs = ps.run('./gradlew copyDependencies'+P_isDebug)
        # outs, errs = ps.run('./gradlew androidDependencies')
    # print('error:', os.linesep, errs)
    # print('output:', os.linesep, outs)
    callback_fun()
    return 

# 创建文件记录引用的所有依赖名称
def F_writeDown_dependsName():
    with PowerShell('GBK') as ps:
        outs, errs = ps.run('./gradlew androidDependencies')
    # print('error:', os.linesep, errs)
    # print('output:', os.linesep, outs)
    # 如果存在文件则删除
    if os.path.isfile(P_FileToStoreDepend):
        os.remove(P_FileToStoreDepend)
    # 存放依赖
    File_dependeSave = open(P_FileToStoreDepend,"w")
    File_dependeSave.write(outs)
    File_dependeSave.close()
    markFlag = 0
    dependeString_begin = 'releaseCompileClasspath'
    dependeString_end = "\\\---"
    File_readDepend = open(P_FileToStoreDepend,"r")
    if os.path.isfile(P_FileTmp):
        os.remove(P_FileTmp)
    File_curTmpFile = open(P_FileTmp,'w')
    for eachLine in File_readDepend:
        if(markFlag == 1):
            File_curTmpFile.write(eachLine[5:])
        if(re.search(dependeString_begin, eachLine)):
            markFlag = 1
        if(re.match(dependeString_end, eachLine)):
            markFlag = 0
    File_readDepend.close()
    File_curTmpFile.close()
    File_dependeSave = open(P_FileToStoreDepend,"w")
    File_curTmpFile = open(P_FileTmp,'r')
    File_dependeSave.write(File_curTmpFile.read())
    File_dependeSave.close()
    File_curTmpFile.close()
    if os.path.isfile(P_FileTmp):
        os.remove(P_FileTmp)
    
    print("creat_dependes_aar_src_end")
    return 

def F_CopyFileFromGradleRoot():
    if(os.path.exists(P_target_jar_inner)):
        shutil.rmtree(P_target_jar_inner)
    if(os.path.exists(P_target_zip)):
        os.remove(P_target_zip)
    os.mkdir(P_target_jar_inner)
    File_readDepend = open(P_FileToStoreDepend,'r')
    for eachLine in File_readDepend:
        srcList = eachLine.split(":")
        curDependAARSrc = P_Gradle_Store_Root + "/" + srcList[0] + "/" + srcList[1] + "/" + srcList[2].split("@")[0]
        
        for curNextSrc in os.listdir(curDependAARSrc):

        # curNextSrc = os.listdir(curDependAARSrc)[0]
            curFinFatherSrc = curDependAARSrc + "/" + curNextSrc
            curAARName = os.listdir(curFinFatherSrc)[0]
            exname = curAARName.split(".")[-1]
            if(exname == "aar" or exname == "jar" and not re.search("-javadoc",curAARName) and not re.search("-sources",curAARName)):
                print(curAARName)
                curFinSrc = curFinFatherSrc + "/" + curAARName
                shutil.copyfile(curFinSrc,P_target_jar_inner+curAARName)
        # print("copy_finish\t"+curAARName)
    File_readDepend.close()
    F_zip_jarclass(P_target_jar,P_target_zip)
    print("creatJar_down")

F_init()
# F_CopyFileFromGradleRoot()