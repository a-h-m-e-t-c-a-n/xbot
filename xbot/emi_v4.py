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
import re

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
    p1=Popen(['avdmanager','create','avd','-n',emi_name,'-k','system-images;android-29;default;x86_64',"--device","19","--sdcard","2048M"],stdin=echono.stdout,env=env)
    p1.wait()
    
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
    os.system('adb remount')
    os.system('adb shell "echo ac.build.id=PPR1.180610.011 >> default.prop"')
    os.system('adb shell "echo ac.build.display.id=PPR1.180610.011.G955FXXSBDUA4 >> default.prop"')
    os.system('adb shell "echo ac.product.name=SM-G955F >> default.prop"')
    os.system('adb shell "echo ac.product.device=dream2lte >> default.prop"')
    os.system('adb shell "echo ac.product.board=universal8895 >> default.prop"')
    os.system('adb shell "echo ac.product.manufacturer=samsung >> default.prop"')
    os.system('adb shell "echo ac.product.brand=samsung >> default.prop"')
    os.system('adb shell "echo ac.product.model=SM-G955F >> default.prop"')
    os.system('adb shell "echo ac.bootloader=G955FXXSBDTK1 >> default.prop"')
    os.system('adb shell "echo ac.hardware=samsungexynos8895 >> default.prop"')
    os.system('adb shell "echo ac.kernel.qemu=0 >> default.prop"')
    os.system('adb shell "echo ac.serial=38bb249aeea613111 >> default.prop"')
    os.system('adb shell "echo ac.build.fingerprint=samsung/dream2ltexx/dream2lte:9/PPR1.180610.011/G955FXXSBDUA4:user/release-keys >> default.prop"')
    os.system('adb reboot')
    emi_waitboot(pemi)
    print("!!!!! cpuinfotext !!!!")
    os.system('adb push s8_cpuinfo.txt /data/s8_cpuinfo.txt')
    os.system('adb shell mount --bind /data/s8_cpuinfo.txt /proc/cpuinfo')

def  emi_set_proxy(addr):
    print(f"emi_set_proxy - >>>>>> http_proxy {addr} >>>>>>>>>>>>")
    #os.system("adb shell settings put global http_proxy 10.0.2.2:9080")
    os.system(f"adb shell settings put global http_proxy {addr}")
    

def emi_run_avd(emi_name):
    #emulator -avd emi1 -writable-system -wipe-data -memory 8192 -no-audio 
    pemi=Popen(["emulator", "-avd", emi_name,"-writable-system","-memory","8192","-no-audio","-no-snapshot"],stdout=PIPE,env=env)
    emi_waitboot(pemi)
    emi_convert_fakedevice(pemi)

def emi_shutdown_avd():
    os.system("adb -e emu kill")
    time.sleep(5)

def emi_copy_userdata(emiid,username):
    avd_home=os.env["ANDROID_AVD_HOME"]
    avd_path=os.join(avd_home,emiid)
    userdata_dir=os.path.join("./userdata",username)
    os.system(f"cp -rf {userdata}/* {avd_path}/")


def emi_install_apk(apkpath):
    print("emi_install_apk")
    return os.system(f"adb install -r {apkpath}")==0

def emi_uninstall_app(pck):
    print("emi_uninstall_app")
    return os.system(f"adb uninstall {pck}")==0

def emi_launch_app(pck):
    os.system(f"adb shell monkey -p {pck} -c android.intent.category.LAUNCHER 1") 


def emi_clearfiles():
    print("!!!!!!!!!!!!!!!!!!!!!!!!!! emi_clearfiles executing  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    os.system("adb shell rm  /storage/emulated/0/Movies/Instagram/*")
    os.system("adb shell rm  /storage/emulated/0/Movies/*")
    os.system("adb shell rm  /storage/emulated/0/Pictures/Instagram/*")
    os.system("adb shell rm  /storage/emulated/0/Pictures/*")
    print("//////////////////! emi_clearfiles finished  //////////////////////////////////////")
    

def emi_avd_exists(name):
    lines=shell_run("emulator -list-avds")
    for avdname in lines:
        print(avdname)
        if  avdname==name:
            return True
    return False
def emi_apk_is_installed(pck): 
    print("emi_apk_is_installed")
    namelist=shell_run("adb shell pm list packages")
    if namelist==None:
        return False
    for name in namelist:
        if name.find(pck)!=-1:
            return True
    return False

def emi_push_media(spath,dpath):
    print("emi_push_media")
    return os.system(f"adb push {spath} /storage/emulated/0/Pictures/{dpath}")==0
 

def emi_runningdevicelist():
    result=[]
    for index,item in enumerate(shell_run("adb devices")):
        if index==0:
            continue
        if item!='':
            result.append(item)
    return result

def emi_allow_externalstorage_permission(pck):
    print("emi_allow_externalstorage_permission will allow permissions")
    os.system(f"adb shell pm grant {pck} android.permission.READ_EXTERNAL_STORAGE")
    os.system(f"adb shell pm grant {pck} android.permission.WRITE_EXTERNAL_STORAGE")
    

#def emi_install_test_apk(apkpath):
#    os.system(f"adb push {apkpath} /data/local/tmp/test.apk")
#    os.system(f"adb shell pm install -t /data/local/tmp/test.apk")
    
def emi_run_test(envparams,pck):
    print("instrument is starting....")
    cmd="adb shell am instrument -w -m -e debug false" 
    for prm in envparams:
        cmd=f"{cmd} -e {prm[0]} {prm[1]} "
    cmd=f"{cmd}  -e class '{pck}.IBotPublishInstagram' {pck}.test/androidx.test.runner.AndroidJUnitRunner"
    
    isfail=shell_run_filter(cmd,"FAILURES")
    if isfail:
        print("!!!!!!! test failed !!!!!!")
        return False
    else:
        print("!!!!!!! test successful !!!!!!")
        return True

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
        
        """
        videofilenames=[os.path.basename(f) for f  in  sorted(glob.glob(os.path.join(idata['dirpath'],"*.mp4")))]
        for basename in videofilenames:
            fn,ext=os.path.splitext(basename)
            os.system(f"ffmpeg -i {os.path.join(idata['dirpath'],basename)} -vcodec copy -acodec copy ./data/{fn}.mkv")            
        """

        emi_clearfiles()
   
        sfiles=[f for f  in  reversed(sorted(glob.glob("./media/*.*")))]
        for index,fname in enumerate(sfiles):
            if emi_push_media(fname,"{:02}{}".format(index,os.path.splitext(fname)[1]))==False:
                raise Exception("adb medyayı emulatore gönderemedi")

        if emi_run_test([("account",account),("password",password)],"xbot.ibot"):
            idata["issuccess"]=True
        else:
            idata["issuccess"]=False
            
        resultlist.append(idata)
        
        if len(data)>1:
            time.sleep(60)
    return resultlist
     
def emi_publish(account,password,data):
    print(f"publish params {account} {password}")
    
    is_diff_account=env.get("INSTA_ACCOUNT")!=account

    env["INSTA_ACCOUNT"]=account 
        
    emi_name="emi0"
    
    emi_shutdown_avd()

    if emi_avd_exists(emi_name)==False:
        emi_create_avd(emi_name)
    
    emi_copy_userdata(emi_name,account)

    emi_run_avd(emi_name)

    emi_set_proxy("10.0.2.2:9080") #tor proxy
    
    #if is_diff_account:
    #   emi_uninstall_app("com.instagram.android")

    #if emi_apk_is_installed("com.instagram.android")==False:
    #    if emi_install_apk(f"./APK/instagram_1800031.apk")==False:
    #        raise Exception("instagram kurulamadı")
    #    emi_install_apk(f"./APK/ibot_app.apk")
    #    emi_install_test_apk(f"./APK/ibot_test.apk")

    emi_launch_app("com.instagram.android")

    return emi_publish_content(account,password,data)
   

"""
adb push xbot.apk /data/local/tmp/
adb shell pm  install -t /data/local/tmp/xbot.apk
adb shell am instrument -w -m  -e debug false -e class 'xbot.ibot.IBotPublishInstagram' xbot.ibot.test/androidx.test.runner.AndroidJUnitRunner
adb get-serialno
adb -s emulator-5554 emu kill
 
 os.system("adb shell avbctl disable-verification")
 os.system("adb disable-verity")
 os.system("adb reboot")
 emi_waitboot(pemi)
 os.system('adb shell "su 0 mount -o rw,remount /system"')
#Popen(["adb","-e","emu","kill"],env=env).wait() #save states
#Popen(["adb","shell","reboot","-p"],env=env).wait()

#curdir= os.path.dirname(os.path.realpath(__file__)) 
adb shell settings put global http_proxy 35.158.57.23:3128
adb shell setprop persist.usb.serialno Phone1_GalaxyS4
adb shell setprop net.hostname ahmethn
adb shell mount --bind /data/s8_cpuinfo.txt /proc/cpuinfo

adb shell input text "mia.on.the.fire"
adb shell input text "gizli80."
adb shell settings put secure location_providers_allowed -gps,network

adb shell pm revoke com.instagram.android android.permission.ACCESS_COARSE_LOCATION
adb shell pm revoke com.instagram.android android.permission.ACCESS_FINE_LOCATION

"""
