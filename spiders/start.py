import sys

sys.path.append("..") 
import asyncio
from free_proxy_list import FPL_Spider
from kuaidaili import KDL_Spider
from xiaohuan import XH_Spider
from redis_check.ip_validate import validate_and_cleanup_proxies
import schedule
import time


async def run_spider():
    fpl_spider = FPL_Spider()
    kdl_spider = KDL_Spider()
    xh_spider = XH_Spider()

    await asyncio.gather(
        fpl_spider.run(),
        kdl_spider.run(),
        xh_spider.run()
    )

async def run_proxy_validation():
    await validate_and_cleanup_proxies()

def schedule_jobs():
    schedule.every().day.at("12:00").do(lambda: asyncio.run(run_spider()))
    schedule.every(10).minutes.do(lambda: asyncio.run(run_proxy_validation()))

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":  
    schedule_jobs()