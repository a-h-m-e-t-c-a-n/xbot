import asyncio
from datetime import datetime, timedelta
import sys
from emi import emi_publish
from taskbase import TaskBase;
import os

class UploadTask(TaskBase):
    def __init__(self):
        super().__init__()
        

    def log(self,subject):
        super().log("download:",subject)

    async def fetch_upload_account(self):
        #return next(self.db.upload_accounts.find({"active":True}).sort([("check_time",-1)]).limit(1),None)
        return self.taskinfo["account"]

    async def update_checktime_upload_account(self,id):
        self.db.upload_accounts.update_one({"_id":id},{"$set":{"check_time":datetime.utcnow()}})

    async def check_profile(self,profile,accept_words,reject_words):
        if profile.get("codes") is None: 
            self.log(f" check_profile no any codes, cancelling match...")
            return True

        codes=profile["codes"]

        if reject_words is not None:
            for reject_and in reject_words: 
                if set(reject_and).issubset(set(codes)):
                    self.log(f" check_profile {profile.get('username')} reject_words check {reject_and} in {codes} matched!")
                    return False

        if accept_words is not None:
            for accept_and in accept_words:
                if set(accept_and).issubset(set(codes)):
                    self.log(f" check_profile {profile.get('username')} accept_words check {accept_and} in {codes} matched!")
                    return True
            self.log(f" check_profile {profile.get('username')} accept_words check {accept_words} in {codes} !!!!not matched")
            return False

        return True

    def download_avd(self,accountid):
        filename=f"{accountid}.zip"
        avdimg_path=os.path.join("avd",filename)

        if os.path.exists(avdimg_path)==False:
            self.copy_file_to_local(avdimg_path,avdimg_path)

    def upload(self,account,uploadlist):
        self.log(f"upload started {account}")
        
        self.download_avd(account["accountid"])
        
        self.purge_mediadir()
        for uploaditem in uploadlist:
            uploaditem["dirpath"]=self.copy_media_to_local(uploaditem["ownerid"],uploaditem["mediaid"])

        completedlist= emi_publish(account["accountid"],account["password"],uploadlist)
        for item in completedlist:
            self.db.download_profiles.update_one({"_id":item["profile"]}, {"$inc":{"uploads."+account["accountid"].replace(".",""):1}},upsert=True)
            self.db.posts.update_one({"_id":item["_id"]}, {"$push":{"shared_accounts":{"account":account["accountid"],"issuccess":item["issuccess"],"date":datetime.utcnow()}}},upsert=True)
        
        return completedlist
 
    async def process_account(self,account):
        uploadlist=[]
        account_id=account["accountid"]
        past_max=account.get("past_max", self.taskinfo.get("u_past_max",0))
        elevation_min=account.get("elevation_min",self.taskinfo.get("u_elevation_min",0))
        like_min=account.get("like_min",self.taskinfo.get("u_like_min",0))
        comment_min=account.get("comment_min",self.taskinfo.get("u_comment_min",0))
        part_max=account.get("part_max",self.taskinfo.get("u_part_max",0))

        query={}
        query["shared_accounts.account"]={"$ne":account_id}
        
        if  past_max>0:
            since = datetime.utcnow() - timedelta(days=past_max)
            query["post_time"]={"$gte":since}
       
        if elevation_min>0:
            query["elevation"]={"$gte":elevation_min}

        if like_min>0:
            query["likes"]={"$gte":like_min}
        
        if comment_min>0:
            query["comments"]={"$gte":comment_min}

       
        agr={}
        agr["$lookup"]={"from":"download_profiles","localField":"profile","foreignField":"_id","as":"OwnerProfile"}
        
        query["OwnerProfile.active"]=True
       
        language=account.get("language")
        if language is not None:
            query["OwnerProfile.language"]=language
  
               
        prm=[agr,{"$match":query},{"$sort":{"OwnerProfile.uploads."+account_id.replace(".",""):1,"elevation":-1}}]

        #if part_max:
            #prm.append({"$limit":part_max})
        
        posts=self.db.posts.aggregate(prm)
       
        for ipost in posts:
            if await self.check_profile(ipost.get("OwnerProfile")[0], account.get("accept"),account.get("reject"))==False:
                self.log(f"process_account check_profile matched {account_id} {ipost['_id']}")
                continue

            self.log(f"a post is found {account_id} {ipost['_id']}")
            comment=None
            caption_hashtags=ipost.get("caption_hashtags")            
            if caption_hashtags is not None and len(caption_hashtags)>0:
                for tag in caption_hashtags:
                    comment=f"{comment or ''}#{tag}\n"
            #uploadlist.append({"_id":ipost["_id"],"dirpath":os.path.join(self.mediapath,ipost["ownerid"],ipost["shortcode"]),"comment":comment,"profile":ipost["profile"]})
            uploadlist.append({"_id":ipost["_id"],"comment":comment,"profile":ipost["profile"],"ownerid":ipost["ownerid"],"mediaid":ipost["shortcode"]})
            if part_max>0 and len(uploadlist)>=part_max:
                self.log(f"process_account part_max matched {account_id} {ipost['_id']}  {len(uploadlist)} > {part_max}")
                break

        return uploadlist
    
    
        
    async def start(self):
        while True: 
            try:
                if self.taskinfo is None:
                    self.log("not taskinfo")
                    await self.wait_next(10)
                    continue
                loop_wait=self.taskinfo.get("loop_wait",60)
                upload_account=await self.fetch_upload_account()
                if upload_account is not None:
                    try:
                        uploadlist=await self.process_account(upload_account)
                        if len(uploadlist)>0:
                            self.upload(upload_account,uploadlist)
                        else:
                            self.log(f"uploadList empty skipping....")
                    except:
                        self.log(f"{upload_account['accountid']} error blocked {sys.exc_info()}")
                    finally:
                        await self.update_checktime_upload_account(upload_account['accountid'])

                    await self.wait_next(loop_wait,1800)
                else:
                    self.log("uploadaccount is not found")
                    await self.wait_next(900)
            except:
                self.log(f"download task error blocked {sys.exc_info()}")
            await self.wait_next(60)





                     