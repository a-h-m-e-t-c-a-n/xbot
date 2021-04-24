from pymongo import MongoClient
import os
from random import randint
from time import sleep
from datetime import datetime, timedelta
import sys
import glob
from subprocess import Popen, PIPE
import threading
import time





env = os.environ.copy()


"""
ANDROID_SDK_ROOT="/home/ahmet/Android/Sdk"
env["ANDROID_EMULATOR_HOME"]="/home/ahmet/.android"
env["ANDROID_AVD_HOME"]="/home/ahmet/.android/avd"
"""

ANDROID_SDK_ROOT="/opt/androidsdk"
env["ANDROID_EMULATOR_HOME"]="/root/.android/"
env["ANDROID_AVD_HOME"]="/root/.android/avd"


env["JAVA_HOME"]="/usr/lib/jvm/java-8-openjdk-amd64/jre"
env["PATH"]=env["PATH"]+":"+ANDROID_SDK_ROOT+"/emulator:"+ANDROID_SDK_ROOT+"/platform-tools:"+ANDROID_SDK_ROOT+"/platform-tools/bin:"+ANDROID_SDK_ROOT+"/tools:"+ANDROID_SDK_ROOT+"/tools/bin"


#env["QTWEBENGINE_DISABLE_SANDBOX"]="1" #önemli -no-sandbox emulator hatası için root altında çalışırken oluşuy9or

#Popen(["adb","-s",emi,"emu","kill"],env=env).wait()

def emi_shutdown():
    Popen(["adb","-e","emu","kill"],env=env).wait() #save states
    #Popen(["adb","shell","reboot","-p"],env=env).wait()
    time.sleep(10)

def emi_clearallprocess():
    count=0
    while count<50:
        ps=Popen(["ps","-A"],stdout=PIPE,env=env)
        ps.wait()
        exist=False
        for line in  ps.stdout.readlines():
            print(line)
            if(line.decode("utf-8").find("qemu")!=-1):
                exist=True
                break
        if exist==False:
            return
        count+=1
        time.sleep(1)

    print("**************qemu will be killed**************")
    Popen(["pkill","qemu*"],env=env).wait()
        

def emi_create(emi_name):
    Popen(['avdmanager','delete','avd','-n',emi_name],env=env).wait()
    echono=Popen(["echo","no"],stdout=PIPE,env=env)
    p1=Popen(['avdmanager','create','avd','-n',emi_name,'-k','system-images;android-30;google_apis_playstore;x86_64','-f',"--device","19","--sdcard","2048M"],stdin=echono.stdout,env=env)
    p1.wait()
  
def emi_run(emi_name):
    #p1=Popen(["emulator", "-avd", emi_name,"-memory","8192","-no-boot-anim","-no-audio","-accel","on","-gpu","swiftshader_indirect"],stdout=PIPE,env=env)
    p1=Popen(["emulator", "-avd", emi_name,"-memory","8192","-no-audio","-accel","on","-gpu","swiftshader_indirect"],stdout=PIPE,env=env)

    """
    p2=Popen(["adb","wait-for-device","shell","getprop","init.svc.bootanim"],stdout=PIPE,env=env)
    p2.wait()
    for line in p2.stdout.readlines():
       print(line)
       if(line.decode("utf-8").find("stopped")!=-1):
          Popen(["adb","shell","input","tap","1081","1420"],env=env).wait()
          Popen(["adb","shell","input","keyevent","82"],env=env).wait()
          time.sleep(10)
          return p1
    """
    count=0
    while True:
        line=p1.stdout.readline()
        print(line)
        #if(line.decode("utf-8").find("completed")!=-1 or  line.decode("utf-8").find("pc_memory_init:")!=-1):
        if(line.decode("utf-8").find("completed")!=-1):
            Popen(["adb","wait-for-device","shell","getprop","init.svc.bootanim"],stdout=PIPE,env=env).wait()
            time.sleep(10)
            Popen(["adb","shell","input","tap","1081","1420"],env=env).wait()
            Popen(["adb","shell","input","keyevent","82"],env=env).wait()
            return p1

        if count>300:
            return None
        count=count+1
        time.sleep(1)
    #return Popen(["emulator", "-avd", name,"-no-boot-anim","-memory","8192","-no-audio","-wipe-data","-accel","on","-gpu","swiftshader_indirect"],env=env)

def emi_install(apkpath,pck):
    Popen(["adb","install",apkpath],env=env).wait() 
    Popen(["adb","shell","monkey","-p",pck,"-c","android.intent.category.LAUNCHER","1"],env=env).wait() 

def emi_clearfiles():
    #Popen(["adb","shell","find","/storage/emulated/0/","-name","*.jpg","-o","-name","*.png","-o","-name","*.mp4","-o","-name","*.mkv","-delete"],env=env).wait() 
    os.system("adb shell rm -r -f /storage/emulated/0/Movies/Instagram/*.mp4")
    os.system("adb shell rm -r -f /storage/emulated/0/Movies/Instagram/*.mkv")
    os.system("adb shell rm -r -f /storage/emulated/0/Movies/*.mp4")
    os.system("adb shell rm -r -f /storage/emulated/0/Movies/*")
    os.system("adb shell rm -r -f /storage/emulated/0/Pictures/Instagram/*.jpg")
    os.system("adb shell rm -r -f /storage/emulated/0/Pictures/Instagram/*.png")
    os.system("adb shell rm -r -f /storage/emulated/0/Pictures/Instagram/*.mp4")
    os.system("adb shell rm -r -f /storage/emulated/0/Pictures/Instagram/*.mkv")
    os.system("adb shell rm -r -f /storage/emulated/0/Pictures/*.jpg")
    os.system("adb shell rm -r -f /storage/emulated/0/Pictures/*.mp4")
    os.system("adb shell rm -r -f /storage/emulated/0/Pictures/*.png")
    os.system("adb shell rm -r -f /storage/emulated/0/Pictures/*")
    

def emi_exists(name):
    cp=Popen(["emulator","-list-avds"],stdout=PIPE,env=env)
    avdlist=cp.stdout.readlines()
    for avdname in avdlist:
        print(avdname)
        if avdname.decode("utf-8").replace("\n", "")==name:
            return True
    return False
def emi_is_installed(pack): 
    cp=Popen(["adb","shell","pm list packages"],stdout=PIPE,env=env)
    cp.wait()
    namelist=cp.stdout.readlines()
    for name in namelist:
        print(name)
        if name.decode("utf-8").find(pack)!=-1:
            return True
    return False

def emi_push_media(spath,dpath):
    Popen(["adb","push",spath,f"/storage/emulated/0/Pictures/{dpath}"],env=env).wait() 
 
#def emi_mediascan(fname):
#     Popen(["adb","shell","am","broadcast","-a","android.intent.action.MEDIA_SCANNER_SCAN_FILE","-d",f"/storage/emulated/0/Pictures"],env=env).wait() 
     #Popen(["adb","shell","am","broadcast","-a","android.intent.action.MEDIA_MOUNTED ","-d","file:///sdcard"],env=env).wait() 

def emi_publish(account,password,data):
    print(f"publish params {account} {password}")

    succeslist=[]
    env["INSTA_ACCOUNT"]=account 
    env["INSTA_PASSWORD"]=password
    
    emi_name=account

    emi_shutdown()
    #emi_clearallprocess()
    
    #if emi_exists(emi_name) == False: silsende geliyordu
    emi_create(emi_name)
    emiprocess=emi_run(emi_name)
    
    #emi_wait()

    if emi_is_installed("com.instagram.android")==False:
        emi_install("./APP/instagram.apk","com.instagram.android")

    curdir= os.path.dirname(os.path.realpath(__file__)) 
    appdir=os.path.join(curdir,"APP")
    olddir=os.getcwd()
    os.chdir(appdir)

    for idata in data:
        os.system(f"rm -r data/*")


        os.system(f"cp {idata['dirpath']}/*.jpg ./data/")
        os.system(f"cp {idata['dirpath']}/*.png ./data/")
        os.system(f"cp {idata['dirpath']}/*.jpeg ./data/")
        #os.system(f"cp {idata['dirpath']}/*.mkv ./data/")

        videofilenames=[os.path.basename(f) for f  in  sorted(glob.glob(os.path.join(idata['dirpath'],"*.mp4")))]
        for fn in videofilenames:
            os.system(f"ffmpeg -i {os.path.join(idata['dirpath'],fn)} -vf vflip -c:a copy ./data/{fn}")
        
        """
        videofilenames=[os.path.basename(f) for f  in  sorted(glob.glob(os.path.join(idata['dirpath'],"*.mp4")))]
        for basename in videofilenames:
            fn,ext=os.path.splitext(basename)
            os.system(f"ffmpeg -i {os.path.join(idata['dirpath'],basename)} -vcodec copy -acodec copy ./data/{fn}.mkv")            
        """

        #emi_clearfiles()
   
        sfiles=[f for f  in  reversed(sorted(glob.glob("./data/*.*")))]
        for index,fname in enumerate(sfiles):
            emi_push_media(fname,f"{index}{os.path.splitext(fname)[1]}")

        res=Popen(["./gradlew","connectedAndroidTest","-i","-Pandroid.testInstrumentationRunnerArguments.account="+account,"-Pandroid.testInstrumentationRunnerArguments.password="+password],env=env).wait() 
        if res==0:
            succeslist.append(idata)
        
        if len(data)>1:
            time.sleep(60)
     

    os.chdir(olddir)
    emi_shutdown()

    emiprocess.wait(60)

    emiprocess.kill()

    

    time.sleep(10)
    return succeslist

