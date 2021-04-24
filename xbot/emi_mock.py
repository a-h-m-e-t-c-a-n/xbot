from pymongo import MongoClient
import os
from random import randint
from time import sleep
import asyncio
from datetime import datetime, timedelta
import sys
import glob
from subprocess import Popen, PIPE
import threading
import time



def publish(account,password,data):
    succeslist=[]

    print(f"publish params {account} {password}")
    ANDROID_SDK_ROOT="/opt/androidsdk"
    #ANDROID_SDK_ROOT="/home/ahmet/Android/Sdk"
    JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/jre"
    
    emi="emi0"
    
    env = os.environ.copy()
    env["INSTA_ACCOUNT"]=account 
    env["INSTA_PASSWORD"]=password
    env["ANDROID_EMULATOR_HOME"]="/root/.android/"
    env["ANDROID_AVD_HOME"]="/root/.android/avd"
    env["JAVA_HOME"]=JAVA_HOME

    env["PATH"]=env["PATH"]+":"+ANDROID_SDK_ROOT+"/emulator:"+ANDROID_SDK_ROOT+"/platform-tools:"+ANDROID_SDK_ROOT+"/platform-tools/bin:"+ANDROID_SDK_ROOT+"/tools:"+ANDROID_SDK_ROOT+"/tools/bin"

    #env["QTWEBENGINE_DISABLE_SANDBOX"]="1" #önemli -no-sandbox emulator hatası için root altında çalışırken oluşuy9or
    
    curdir= os.path.dirname(os.path.realpath(__file__)) 
    appdir=os.path.join(curdir,"APP")
    olddir=os.getcwd()
    os.chdir(appdir)


    #Popen(["adb","-s",emi,"emu","kill"],env=env).wait()
    Popen(["adb","shell","reboot","-p"],env=env).wait()

    Popen(['avdmanager','delete','avd','-n',emi],env=env).wait()


    p2=Popen(["echo","no"],stdout=PIPE,env=env)
    
    #avdmanager create avd -n emi3 -k 'system-images;android-30;google_apis_playstore;x86_64' -f --tag "google_apis_playstore"  --device 19  --sdcard 256M

    p1=Popen(['avdmanager','create','avd','-n',emi,'-k','system-images;android-30;google_apis_playstore;x86_64','-f',"--device","19","--sdcard","1024M"],stdin=p2.stdout,env=env)
    #p1=Popen(['avdmanager','create','avd','-n','emi','-k','system-images;android-30;google_apis_playstore;x86_64','-f'],stdin=p2.stdout,env=env)
    p1.wait()
    
        

    emiprocess=Popen(["emulator", "-avd", emi,"-memory","8192","-no-audio","-wipe-data","-accel","on","-gpu","swiftshader_indirect"],env=env)
      
    
    Popen(["adb","wait-for-device","shell","getprop","init.svc.bootanim"],env=env).wait()

    Popen(["adb","shell","input","keyevent","82"],env=env).wait()
    time.sleep(1)
    Popen(["adb","shell","input","tap","1081","1420"],env=env).wait()
    time.sleep(1)
    Popen(["adb","shell","input","keyevent","82"],env=env).wait()
    time.sleep(1)
    Popen(["adb","shell","input","tap","1081","1420"],env=env).wait()
    time.sleep(1)

    Popen(["adb","install","./instagram.apk"],env=env).wait() 
    Popen(["adb","shell","monkey","-p","com.instagram.android","-c","android.intent.category.LAUNCHER","1"],env=env).wait() 

    for idata in data:
        os.system(f"rm -r data/*")


        os.system(f"cp {idata['dirpath']}/*.jpg ./data/")
        os.system(f"cp {idata['dirpath']}/*.png ./data/")
        os.system(f"cp {idata['dirpath']}/*.jpeg ./data/")

        videofilenames=[os.path.basename(f) for f  in  sorted(glob.glob(os.path.join(idata['dirpath'],"*.mp4")))]
        for fn in videofilenames:
            os.system(f"ffmpeg -i {os.path.join(idata['dirpath'],fn)} -vf vflip -c:a copy ./data/{fn}")

        Popen(["adb","shell","find","/storage/emulated/0/","-name","*.jpg","-o","-name","*.png","-o","-name","*.mp4","-delete"],env=env).wait() 
        Popen(["adb","shell","rm","-r","/storage/emulated/0/Pictures/*"],env=env).wait() 
        
        sfiles=[f for f  in  sorted(glob.glob("./data/*.*"))]
        for fpath in sfiles:
            Popen(["adb","push",fpath,"/storage/emulated/0/Pictures"],env=env).wait() 
    
        res=Popen(["./gradlew","connectedAndroidTest","-i","-Pandroid.testInstrumentationRunnerArguments.account="+account,"-Pandroid.testInstrumentationRunnerArguments.password="+password],env=env).wait() 
        if res==0:
            succeslist.append(idata)
     

    os.chdir(olddir)
    Popen(["adb","shell","reboot","-p"],env=env).wait()
    time.sleep(10)
    emiprocess.kill()
    return succeslist

