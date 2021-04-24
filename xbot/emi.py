from pymongo import MongoClient
from random import randint
from time import sleep
from datetime import datetime, timedelta
import sys
import glob
from subprocess import Popen, PIPE
import threading
import time
import re
import os

env = os.environ


"""
ANDROID_SDK_ROOT="/home/ahmet/Android/Sdk"
env["ANDROID_EMULATOR_HOME"]=env.get("ANDROID_EMULATOR_HOME","/home/ahmet/.android")
env["ANDROID_AVD_HOME"]=env.get("ANDROID_AVD_HOME","/home/ahmet/.android/avd")
"""
ANDROID_SDK_ROOT="/opt/androidsdk"
env["ANDROID_EMULATOR_HOME"]=env.get("ANDROID_EMULATOR_HOME","/root/.android")
env["ANDROID_AVD_HOME"]=env.get("ANDROID_AVD_HOME","/root/.android/avd")


env["JAVA_HOME"]="/usr/lib/jvm/java-8-openjdk-amd64/jre"
if ("platform-tools" in env["PATH"]) == False:
    env["PATH"]=ANDROID_SDK_ROOT+"/emulator:"+ANDROID_SDK_ROOT+"/platform-tools:"+ANDROID_SDK_ROOT+"/platform-tools/bin:"+ANDROID_SDK_ROOT+"/tools:"+ANDROID_SDK_ROOT+"/tools/bin"+":"+env["PATH"]


env["QTWEBENGINE_DISABLE_SANDBOX"]="1" #önemli -no-sandbox emulator hatası için root altında çalışırken oluşuy9or

#Popen(["adb","-s",emi,"emu","kill"],env=env).wait()
def shell_run_filter(cmd,filterword,timeout=None):
    cmdarr=cmd.split(" ")
    pcmd=Popen(cmdarr,stdout=PIPE,env=env)
    
    filter_occured=False
    for line in pcmd.stdout.readlines():
        #print(line)
        try:
            if  re.search(filterword,line.decode("utf-8").replace("\n", ""),flags=re.IGNORECASE):
                filter_occured=True
                break
        except:
            pass

    if timeout:
        pcmd.wait(timeout)
    else:
        pcmd.wait()
    return filter_occured

def shell_run(cmd,timeout=None):
    cmdarr=cmd.split(" ")
    pcmd=Popen(cmdarr,stdout=PIPE,env=env)
    
    result=[]
    for line in pcmd.stdout.readlines():
        try:
            result.append(line.decode("utf-8").replace("\n", ""))
        except:
            pass

    if timeout:
        pcmd.wait(timeout)
    else:
        pcmd.wait()

    return result
    


def emi_create_avd(emi_name):
    #avdmanager create avd -n emi1 -k "system-images;android-29;default;x86_64" -f --device 19 --sdcard 2048M
    os.system(f"avdmanager delete avd -n {emi_name}")
    echono=Popen(["echo","no"],stdout=PIPE,env=env)
    p1=Popen(['avdmanager','create','avd','-n',emi_name,'-k','system-images;android-29;default;x86_64',"--device","19","--sdcard","800M"],stdin=echono.stdout,env=env)
    p1.wait()
    emi_run_avd(emi_name)
    emi_shutdown_avd()
    
def emi_waitboot(pemi):
    for count in range(0,300):
        line=pemi.stdout.readline()
        print(line)
        if(line.decode("utf-8").find("completed")!=-1):
            Popen(["adb","wait-for-device","shell","getprop","init.svc.bootanim"],stdout=PIPE,env=env).wait()
            time.sleep(3)
            return True
        time.sleep(1)
    return False

def  emi_convert_fakedevice(pemi):
    print("!!!!! build.props !!!!")
    os.system('adb push props/local.prop /data/local.prop')
    os.system('adb shell chmod 644 /data/local.prop')
    os.system('adb reboot')
    emi_waitboot(pemi)
    print("!!!!! cpuinfotext !!!!")
    os.system('adb push  props/cpu.txt /data/cpu.txt')
    os.system('adb shell mount --bind /data/cpu.txt /proc/cpuinfo')

def  emi_set_proxy(addr):
    print(f"emi_set_proxy - >>>>>> http_proxy {addr} >>>>>>>>>>>>")
    #os.system("adb shell settings put global http_proxy 10.0.2.2:9080")
    os.system(f"adb shell settings put global http_proxy {addr}")
    

def emi_run_avd(emi_name):
    #emulator -avd emi1 -writable-system -wipe-data -memory 8192 -no-audio 
    #pemi=Popen(["emulator", "-avd", emi_name,"-writable-system","-memory","8192","-no-audio","-no-snapshot"],stdout=PIPE,env=env)
    pemi=Popen(["emulator", "-avd", emi_name,"-memory","2048","-no-audio","-no-snapshot"],stdout=PIPE,env=env)
    emi_waitboot(pemi)
    return pemi

def emi_shutdown_avd():
    os.system("adb -e emu kill")
    time.sleep(5)

def emi_reset_userdata(emiid,username):
    avd_home=env["ANDROID_AVD_HOME"]
    avd_dir_path=os.path.join(avd_home,f"{emiid}.avd")
    avd_ini_path=os.path.join(avd_home,f"{emiid}.ini")
    userdata_fn=os.path.join(f"{username}.zip")
    userdata_path=os.path.join("./avd",userdata_fn)

    os.system(f"rm -r {avd_dir_path}")
    os.system(f"rm  {avd_ini_path}")
    print(f"{userdata_fn}/* {avd_dir_path}/ extracting....")
    os.system(f"unzip {userdata_path} -d {avd_home}")


def emi_launch_app(pck):
    os.system(f"adb shell monkey -p {pck} -c android.intent.category.LAUNCHER 1") 


def emi_clearfiles():
    print("!!!!!!!!!!!!!!!!!!!!!!!!!! emi_clearfiles executing  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    os.system("adb shell rm  /storage/emulated/0/Movies/Instagram/*")
    os.system("adb shell rm  /storage/emulated/0/Movies/*")
    os.system("adb shell rm  /storage/emulated/0/Pictures/Instagram/*")
    os.system("adb shell rm  /storage/emulated/0/Pictures/*")
    print("//////////////////! emi_clearfiles finished  //////////////////////////////////////")

def emi_set_permissions():
    os.system(f"adb shell pm revoke com.instagram.android android.permission.ACCESS_COARSE_LOCATION")
    os.system(f"adb shell pm revoke com.instagram.android android.permission.ACCESS_FINE_LOCATION")
    os.system(f"adb shell pm revoke com.instagram.android android.permission.PHONE")

def emi_avd_exists(name):
    lines=shell_run("emulator -list-avds")
    for avdname in lines:
        print(avdname)
        if  avdname==name:
            return True
    return False


def emi_push_media(spath,dpath):
    print("emi_push_media")
    return os.system(f"adb push {spath} /storage/emulated/0/Pictures/{dpath}")==0
 
   
def emi_run_instrument(envparams,pck):
    print("instrument is starting....")
    cmd="adb shell am instrument -w -m -e debug false" 
    for prm in envparams:
        cmd=f"{cmd} -e {prm[0]} {prm[1]} "
    cmd=f"{cmd}  -e class '{pck}.IBotPublishInstagram' {pck}.test/androidx.test.runner.AndroidJUnitRunner"
    
    print(cmd)

    isfail=shell_run_filter(cmd,"FAILURES")
    if isfail:
        print("!!!!!!! instrument failed !!!!!!")
        return False
    else:
        print("!!!!!!! instrument successful !!!!!!")
        return True

def emi_runningdevicelist():
    result=[]
    for index,item in enumerate(shell_run("adb devices")):
        if index==0:
            continue
        if item!='':
            result.append(item)
    return result

def emi_any_device_running():
    return (len(emi_runningdevicelist())>0)

def emi_publish_content(account,password,data):
    resultlist=[]
    for idata in data:
        os.system(f"rm -r ./media/*")


        os.system(f"cp {idata['dirpath']}/*.jpg ./media/")
        os.system(f"cp {idata['dirpath']}/*.png ./media/")
        os.system(f"cp {idata['dirpath']}/*.jpeg ./media/")
        
        videofilenames=[os.path.basename(f) for f  in  sorted(glob.glob(os.path.join(idata['dirpath'],"*.mp4")))]
        for fn in videofilenames:
            os.system(f"ffmpeg -i {os.path.join(idata['dirpath'],fn)} -vf vflip -c:a copy ./media/{fn}")
        

        emi_clearfiles()
   
        sfiles=[f for f  in  reversed(sorted(glob.glob("./media/*.*")))]
        for index,fname in enumerate(sfiles):
            if emi_push_media(fname,"{:02}{}".format(index,os.path.splitext(fname)[1]))==False:
                raise Exception("adb medyayı emulatore gönderemedi")
        
        instrumentparams=[("account",account),("password",password)]
        if idata.get("comment"):
            instrumentparams.append(("content",f"'{idata['comment']}'"))

        if emi_run_instrument(instrumentparams,"xbot.ibot"):
            idata["issuccess"]=True
            print("waiting 120 seconds.....")
            time.sleep(120)
        else:
            idata["issuccess"]=False
            
        resultlist.append(idata)
        
        if len(data)>1:
            time.sleep(60)
    return resultlist
     
def emi_publish(account,password,data):
    print(f"publish params {account} {password}")

    emi_name="emi"
    
    if emi_avd_exists(emi_name)==False:
        emi_shutdown_avd()
        emi_create_avd(emi_name)
    
    if emi_any_device_running()==False:        
        emi_reset_userdata(emi_name,account)
        pemi=emi_run_avd(emi_name)
        emi_convert_fakedevice(pemi)

    #emi_set_proxy("10.0.2.2:9080") #tor proxy
    time.sleep(5)       
    emi_launch_app("com.instagram.android")
    time.sleep(5)       
    emi_launch_app("com.instagram.android")

    result=emi_publish_content(account,password,data)

    return result

def emi_run_normal(userid,password):
    emi_name="emi"
    
    if emi_avd_exists(emi_name)==False:
        emi_create_avd(emi_name)
    

    emi_reset_userdata(emi_name,userid)
    pemi=emi_run_avd(emi_name)
    emi_convert_fakedevice(pemi)
    
    emi_set_permissions()

    time.sleep(5)       
    emi_launch_app("com.instagram.android")
    time.sleep(5)       
    emi_launch_app("com.instagram.android")
    time.sleep(1)
    
    if userid:
        os.system("adb shell input tap 500 1000")
        for i in range(0,100):
            os.system("adb shell input keyevent KEYCODE_DEL")
    
        time.sleep(1)
        os.system(f"adb shell input text '{userid}'")
        time.sleep(1)
        os.system("adb shell input tap 500 850")
        time.sleep(1)
        os.system(f"adb shell input text '{password}'")
    
    

    


   
   
