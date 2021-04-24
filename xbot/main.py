from pymongo import MongoClient
from datetime import datetime
import os
import sys
import asyncio
from download import DownloadTask
from upload import UploadTask
import math
#env variables
#MEDIA_PATH video download path
#MONGO_CONN database conn
#WORKERID worker id


env_workerid=os.environ['WORKERID']
env_country=os.environ.get('COUNTRY',"-")

print("--------MONGO_CON----------> %s" % os.environ.get("MONGO_CONN","mongodb://root:1@localhost:27017/"))

print(env_workerid)
def init_db():
    dbconnection=os.environ.get("MONGO_CONN","mongodb://root:1@localhost:27017/")
    global client
    global db
    client = MongoClient(dbconnection)
    db=client.bot

init_db()

downloadTask=DownloadTask()
uploadTask=UploadTask()

async def main():
    currentdownloadtask=None
    currentuploadtask=None
    iteration=0
    while True:
        try:
            if uploadTask.time_ref is not None and iteration%6==0:
                remain_seconds=uploadTask.time_count-(datetime.utcnow()-uploadTask.time_ref).total_seconds()
                print(f"uploadtask remaining {math.ceil(remain_seconds/60)} min")
            if downloadTask.time_ref is not None and iteration%6==0:
                remain_seconds=downloadTask.time_count-(datetime.utcnow()-downloadTask.time_ref).total_seconds()
                print(f"downloadtask remaining {math.ceil(remain_seconds/60)} min")

            db.workers.update_one({"_id":env_workerid},{ "$set":{"country":env_country,"last_seen":datetime.now()}},upsert=True)

            workerinfo=db.workers.find_one({"_id":env_workerid})

            if workerinfo.get("download",False)==False:
                currentdownloadtask=None
            else:
                if currentdownloadtask is None:
                    currentdownloadtask=asyncio.create_task(downloadTask.start())
            
            if workerinfo.get("upload",False)==False:
                currentuploadtask=None
            else:
                if currentuploadtask is None:
                    currentuploadtask=asyncio.create_task(uploadTask.start())

            downloadTask.setTaskInfo(workerinfo.get("DownloadTaskInfo"))
            uploadTask.setTaskInfo(workerinfo.get("UploadTaskInfo"))

            await asyncio.sleep(10)
            iteration+=1
        except:
            try:
                client.close()
            except:
                print("conn close error")
            
            print(sys.exc_info())
            await asyncio.sleep(1)
            init_db()
            

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
result = loop.run_until_complete(main())    

