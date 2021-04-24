import asyncio
import  emi
import sys

async def main():
    if len(sys.argv)>1:
        emi.emi_run_normal(sys.argv[1],sys.argv[2])
    else:
        emi.emi_run_normal(None,None)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main())    
