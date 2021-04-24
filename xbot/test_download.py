import asyncio
import  download


async def main():
    task=download.DownloadTask()
    await task.start()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main())    
