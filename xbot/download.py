import instaloader
import os
import asyncio
from datetime import datetime, timedelta
import sys
import math
from langdetect import detect
from taskbase import TaskBase;
import pathlib

class DownloadTask(TaskBase):
    def __init__(self):
        super().__init__()

    def init_loader(self,use_tor):
        if use_tor:
            self.L = instaloader.Instaloader(proxies={
                        "http": "http://127.0.0.1:9080",
                        "https": "http://127.0.0.1:9080",
                    })
        else:
            self.L = instaloader.Instaloader()

        self.L.filename_pattern="media"
        self.L.download_video_thumbnails=False

    async def fetch_download_account(self):
        result=next(self.db.download_accounts.find({"active":True}).sort([("check_time",1)]).limit(1),None)
        self.db.download_accounts.update_one({"_id":result["_id"]},{"$set":{"check_time":datetime.utcnow()}})

        return result


    def log(self,subject):
        super().log("download:",subject)

    async def refresh_login(self):
        account=await self.fetch_download_account()
        self.log(f"refresh_login {account['id']} is logging....")
        try:
            self.L.load_session_from_file(account['id'],f"instaload_sessions/{account['id']}")
            if self.L.context.is_logged_in == False:
                self.L.login(account["id"],account["password"])        
                self.L.save_session_to_file(f"instaload_sessions/{account['id']}")
                #L.interactive_login(USER)      # (ask password on terminal)
                #L.load_session_from_file(USER) # (load session created w/
        except instaloader.exceptions.TooManyRequestsException:
            raise instaloader.exceptions.TooManyRequestsException(f"refresh login blocked {sys.exc_info()[0]}")
        except:
            self.log(f"{account['id']} refresh login error blocked {sys.exc_info()[1]} {sys.exc_info()[2].tb_lineno}")
            self.L.login(account["id"],account["password"])        
            self.L.save_session_to_file(f"instaload_sessions/{account['id']}")
     
    async def fetch_profile(self):
        result=next(self.db.download_profiles.find({"active":True}).sort([("check_time",1)]).limit(1),None)
        if result:
            self.db.download_profiles.update_one({"_id":result["_id"]},{"$set":{"check_time":datetime.utcnow()}})
        return result
    
    async def fetch_hashtag(self):
        result=next(self.db.download_hashtag.find({"active":True}).sort([("check_time",1)]).limit(1),None)
        if result:
            self.db.download_hashtag.update_one({"_id":result["_id"]},{"$set":{"check_time":datetime.utcnow()}})
        return result

    def filter_post(self,post,profileinfo):
        like_min=profileinfo.get("like_min",self.taskinfo.get("d_like_min",0))
        comment_min=profileinfo.get("comment_min",self.taskinfo.get("d_comment_min",0))
        elevation_min=profileinfo.get("elevation_min",self.taskinfo.get("d_elevation_min",0))

        elevation=self.calc_elevation(post.date_utc,post.comments,post.likes)
        self.log(f"filter_post {profileinfo.get('id')} elevation:{elevation} comments:{post.comments} likes:{post.likes}")
        if like_min>0:
            if post.likes<like_min:
                self.log(f"filter_post like_min matched {post.likes}<{like_min}")
                return False
        if comment_min>0:
            if post.comments<comment_min:
                self.log(f"filter_post comment_min matched {post.comments}<{comment_min}")
                return False
        if elevation_min>0:
            if  elevation<elevation_min:
                self.log(f"filter_post elevation_min matched {elevation}<{elevation_min}")
                return False
        return True

    def filter_hashtag(self,media,hashtaginfo):
        like_min=hashtaginfo.get("like_min", self.taskinfo.get("t_like_min",0))
        comment_min=hashtaginfo.get("comment_min",self.taskinfo.get("t_comment_min",0))
        elevation_min=hashtaginfo.get("elevation_min",self.taskinfo.get("t_elevation_min",0))

        if like_min>0:
            if media.likes<like_min:
                return False
        if comment_min>0:
            if media.comments<comment_min:
                return False
        if elevation_min>0:
            elevation=self.calc_elevation(media.date_utc, media.comments,media.likes)
            if elevation <elevation_min:
                return False
        return True

    def download_media(self,post):
        self.L.download_post(post, pathlib.Path(self.get_media_path(post.owner_id,post.shortcode)))
        self.copy_media_to_remote(post.owner_id,post.shortcode)

    def detect_language(self,profile):
        try:
            return detect(profile.biography)
        except:
            return ""

    async def update_profile(self,profile,caption=None):
        now=datetime.utcnow()
        
        language=self.detect_language(profile)

        profile_data = {
                "language":language,
                "biography":profile.biography,
                "followees":profile.followees,
                "followers":profile.followers,
                "full_name":profile.full_name,
                "is_private":profile.is_private,
                "mediacount":profile.mediacount,
                "profile_pic_url":profile.profile_pic_url,
                "owner_id":profile.userid,
                "username":profile.username
           
            }
        self.db.download_profiles.update_one({"_id":profile.username},{"$set":{"update_time":datetime.utcnow(),"pulled": profile_data }},upsert=True)
        self.log(f"{profile.username} {profile.biography} {profile.followers} {language} ACCEPTED")
    
    async def update_profile_byownerid(self,owner_id,key,followers_min=None,followers_max=None):

        if followers_min is None:
            followers_min=self.taskinfo.get("followers_min",0)

        if followers_max is None:
            followers_max=self.taskinfo.get("followers_max",0)

        profiledb=self.db.download_profiles.find_one({"owner_id":owner_id})
        exists=profiledb is not None

        if exists:        
            if ((datetime.utcnow()-profiledb.get("update_time",datetime.min)).total_seconds()/3600)<24:
                return
            if key in profiledb["sources"] == False:
                self.db.download_profiles.update_one({"owner_id":owner_id},{"$push":{"sources":f"#{key}"}},upsert=True)    


        profile=instaloader.Profile.from_id(self.L.context,owner_id)

        if followers_min>0 and profile.followers<followers_min:
           self.log(f"update_profile_byownerid {profile.username} followers_min matched {profile.followers} < {followers_min}")
           return
        
        if followers_max>0 and profile.followers>followers_max:
            self.log(f"update_profile_byownerid {profile.username} followers_max matched {profile.followers} > {followers_max}")
            return

        if exists==False:
            self.db.download_profiles.update_one({"_id":profile.username},{"$set":{"_id":profile.username,"owner_id":owner_id,"create_time":datetime.utcnow(),"sources":[f"#{key}"]}},upsert=True)

        self.log(f"update_profile_byname {profile}")
        await self.update_profile(profile,None)

    def calc_elevation(self,postdate,comments,likes):
        total_hour=((datetime.utcnow()-postdate).total_seconds()/3600)
        elevation=math.ceil((comments+likes)/total_hour)
        return elevation


    async def accept_post(self,post):
        self.log("accept_post executing ........")
        now=datetime.utcnow()
        result=False
        post_data={"mediaid":post.mediaid,
                   "title":post.title,
                   "caption":post.caption,
                   "comments":post.comments,
                   "likes":post.likes,
                   "mediacount":post.mediacount,
                   "location":post.location,
                   "ownerid":post.owner_id,
                   "profile":post.profile,
                   "shortcode":post.shortcode,
                   "url":post.url,
                   "video_url":post.video_url,
                   "video_view_count":post.video_view_count,
                   "viewer_has_liked":post.viewer_has_liked,
                   "video_duration":post.video_duration,
                   "is_video":post.is_video,
                   "is_sponsored":post.is_sponsored,
                   "sponsor_users":post.sponsor_users,
                   "tagged_users":post.tagged_users,
                   "caption_mentions":post.caption_mentions,
                   "caption_hashtags":post.caption_hashtags,
                   "typename":post.typename,
                   "update_time":now,
                   "post_time":post.date_utc,
                   "elevation":0,
                   "elevation":self.calc_elevation(post.date_utc,post.comments,post.likes)

        }
        try:
            if post.location:
                post_data["location"]={"name":post.location.name,"slug":post.location.slug,"lat":post.location.lat,"lng":post.location.lng}
        except:
            pass

        post_old=self.db.posts.find_one({"_id":post.shortcode})
        if post_old is None:
            self.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!accept_post started to download!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.download_media(post)
            self.log("------------------------------------accept_post download finished ----------------------------------------------------")
            result=True
        else:
           post_data={"comments":post.comments,"likes":post.likes,"elevation":self.calc_elevation(post.date_utc,post.comments,post.likes)}

        self.db.posts.update_one({"_id":post.shortcode},{"$set":post_data},upsert=True)
        return result

    async def process_profile(self,profileinfo):
        profile=instaloader.Profile.from_username(self.L.context,profileinfo["_id"])
        await self.update_profile(profile)
        self.log("instgaloader profile fetched")
        count_limit=profileinfo.get("count_limit",self.taskinfo.get("d_count_limit",0))
        past_max=profileinfo.get("past_max",self.taskinfo.get("d_past_max",0))

        total_count=0
        for post in profile.get_posts():
            self.log(f"process_profile {profileinfo.get('_id')} post >  {post.shortcode} comments:{post.comments} likes:{post.likes} video:{post.is_video} {post.date_utc} ddays:{(datetime.utcnow()-post.date_utc).days} {post.caption}")
            if past_max>0:
                dday=((datetime.utcnow()-post.date_utc).total_seconds()/86400)
                if dday>past_max:
                    self.log(f"process_profile {profileinfo.get('_id')} past_max matched {dday}>{past_max}")
                    break
            if count_limit>0:
                if total_count>count_limit:
                    self.log(f"process_profile {profileinfo.get('_id')} count_limit matched {total_count}>{count_limit}")
                    break
            if(self.filter_post(post,profileinfo)):
                if await self.accept_post(post):
                   total_count+=0
                   await self.wait_next(3,30)
            else:
                self.log("filter passed")
    
    async def process_tag(self,hashtaginfo):
        self.log("process_tag executing")
        allmedia=[]
        try:
            hashtag=instaloader.Hashtag.from_name(self.L.context,hashtaginfo["tag"])
            allmedia.extend(hashtag.get_media())
        except:
            hashtag=instaloader.Hashtag.from_name_v2(self.L.context,hashtaginfo["tag"])
            allmedia.extend(hashtag.get_media_v2())
        
        count_max=hashtaginfo.get("count_max",self.taskinfo.get("t_count_max",0))

        for index,media in  enumerate(sorted(allmedia, key=lambda p: p.likes, reverse=True)):
            try:
                if count_max>0:
                    if index>count_max:
                        self.log(f"{count_max} {index} count_max break")
                        break

                self.log(f"{index+1}/{len(allmedia)} -> {media.id}  comments:{media.comments} likes:{media.likes}")
                
                if(self.filter_hashtag(media,hashtaginfo)):
                    await self.update_profile_byownerid(media.owner_id,hashtaginfo["tag"],hashtaginfo.get("followers_min"),hashtaginfo.get("followers_max"))
                    self.db.download_hashtag.update_one({"_id":hashtaginfo["_id"]},{"$set":{"update_time": datetime.utcnow()}},upsert=True)
                else:
                    self.log("filter passed")
            except instaloader.exceptions.TooManyRequestsException:
                raise instaloader.exceptions.TooManyRequestsException(f"process_tag loop {media.id}  error blocked {sys.exc_info()[0]}")
            except:
                self.log(f"process_tag loop {media.id}  error blocked {sys.exc_info()[0]}")
                self.log(f"process_tag loop {media.id}  error blocked {sys.exc_info()[1]} {sys.exc_info()[2].tb_lineno}")


    async def exec_tag(self):
        await self.refresh_login()
        
        hashtaginfo=await self.fetch_hashtag()
        if hashtaginfo is None:
            return False
        try:
            await self.process_tag(hashtaginfo)
        except instaloader.exceptions.LoginRequiredException:
            print("******************Login İstiyor-------------------------------")
        
        except instaloader.exceptions.TooManyRequestsException:
                raise instaloader.exceptions.TooManyRequestsException(f"exec_tag blocked {sys.exc_info()[0]}")
        except:
            self.log(f"{hashtaginfo['tag']} error blocked {sys.exc_info()[0]}")
            self.log(f"{hashtaginfo['tag']} error blocked {sys.exc_info()[1]} {sys.exc_info()[2].tb_lineno}")
        finally:
            self.db.download_hashtag.update_one({"_id":hashtaginfo["_id"]},{"$set":{"check_time":datetime.utcnow()}})
        return True

    async def exec_profile(self):
        await self.refresh_login()
        profileinfo=await self.fetch_profile()
        try:
            self.log(f"*********************************** {profileinfo['_id']} ********************************************")
            await self.process_profile(profileinfo)
        except:
            self.log(f"{profileinfo['_id']} error blocked {sys.exc_info()[1]} {sys.exc_info()[2].tb_lineno}")
        
    async def start(self):
        while True:
            try:
                if self.taskinfo is None: 
                    await self.wait_next(10)
                    continue

                self.download_tor=self.taskinfo.get("download_tor",False)  
                self.init_loader(self.download_tor) 

                
                hashtag_active=self.taskinfo.get("hashtag_active",False)
                post_active=self.taskinfo.get("post_active",False)
                next_process_wait=self.taskinfo.get("next_process_wait",120)
                toomany_wait=self.taskinfo.get("toomany_wait",3600)

                if hashtag_active:
                    await self.exec_tag()
              
                if post_active:
                    await self.exec_profile()

                await self.wait_next(next_process_wait)

            except instaloader.exceptions.TooManyRequestsException:
                self.log(f"-!-!--!-!--!-!--!-!--!-!--!-!-TOO MANY REQUEST-!-!--!-!--!-!--!-!--!-!--!-!--!-!--!-")
                await self.wait_next(toomany_wait)
            except:
                self.log(f"general error blocked {sys.exc_info()[0]}")
                self.log(f"general error blocked {sys.exc_info()[1]} {sys.exc_info()[2].tb_lineno}")
                await self.wait_next(60)
        

    


