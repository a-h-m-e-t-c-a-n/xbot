import asyncio
import  upload


async def main():
    task=upload.UploadTask()
    #task.download_avd("user1")
    #print(task.get_media_path("userid1","media1"))
    #print(task.copy_media_to_remote("user1","media1"))
    #print(task.copy_media_to_local("user1","media1"))
    #print(task.purge_mediadir())
    taskinfo={""}
    await task.start()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main())    
