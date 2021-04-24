from pymongo import MongoClient
from random import randint
import time
import asyncio
from datetime import datetime, timedelta
import sys
import math
from pathlib import Path
import os

class TaskBase:
    def __init__(self):
        self.taskinfo=None
        dbconnection=os.environ.get("MONGO_CONN","mongodb://root:1@localhost:27017/")
        self.s3_url= os.environ.get('S3_URL')
        self.client = MongoClient(dbconnection)
        self.db=self.client.bot
        self.time_ref=None
        self.time_count=0
  
    def setTaskInfo(self,taskinfo):
        self.taskinfo=taskinfo

    def log(self,tag,subject):
        print(f"{tag}: {subject}")
    
    def get_media_path(self,ownerid,mediaid):
        return os.path.join("media",ownerid,mediaid) 

    def copy_file_to_local(self,remotepath,localpath):
        s3_remotepath=os.path.join(self.s3_url,remotepath)
        if os.system(f"aws s3 cp {s3_remotepath} {localpath}") !=0:
            raise Exception("copy_file_to_local s3 media download error")
        return localpath

    def copy_media_to_local(self,ownerid,mediaid):
        s3_remotepath=os.path.join(self.s3_url,"media",ownerid,mediaid)
        localpath=self.get_media_path(ownerid,mediaid)
        if os.system(f"aws s3 cp --recursive {s3_remotepath} {localpath}") != 0:
            raise Exception("copy_media_to_local s3 media download error")
        return localpath

    def copy_media_to_remote(self,ownerid,mediaid):
        s3_remotepath=os.path.join(self.s3_url,"media",ownerid,mediaid)
        localpath=self.get_media_path(ownerid,mediaid)
        os.system(f"aws s3 cp --recursive {localpath} {s3_remotepath}")
        return localpath

    def purge_mediadir(self):
         os.system(f"rm -r media/*")
    
    def calc_elevation(self,postdate,comments,likes):
        total_hour=((datetime.utcnow()-postdate).total_seconds()/3600)
        elevation=math.ceil((comments+likes)/total_hour)
        return elevation


    async def wait_next(self,seconds,range_second=None):
        self.time_ref=datetime.utcnow()
        if range_second:
            self.time_count=randint(seconds,seconds+range_second)
            self.log(f"wait_next waiting for  processing  {self.time_count} seconds")
            await asyncio.sleep(self.time_count)   
        else:
            self.time_count=seconds
            self.log(f"wait_next waiting for  processing  {self.time_count} seconds")
            await asyncio.sleep(self.time_count)   
        self.time_ref=None    


    def exit(self, *err):
        self.client.close()



