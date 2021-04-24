import asyncio
import  emi

async def main():
    #emi_install_instagram("./APP/instagram.apk")
    #emi_clearfiles()
    #emi_push_media("/media/ahmet/secondary/workspace/graphics/dragoman graphics/1.jpg")

    #params=[{"dirpath":"/files/11875441539/CNre6uBBU4k","comment":None}]
    #emi.emi_publish("jessybiotic", "gizli80.", params)
    #emi.userdata_dir("emi0","jessybiotic")
    #while True:
    #   publish("girlinthefire", "uyelik", None, "/media/ahmet/workspace/source/bot/xbot/APP/samples")
        #publish("rythimzero", "social8019.", None, "/files/1419706373/CM0HnqxhHRH")
    
    emi.emi_reset_userdata("emi","user1")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main())    
