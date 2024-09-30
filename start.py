from spiders.free_proxy_list import FPL_Spider
from spiders.kuaidaili import KDL_Spider
from redis_check.ip_validate import validate_and_cleanup_proxies
from spiders.xiaohuan import XH_Spider

if __name__ == "__main__":  
    import schedule
    import time

    @schedule.repeat(schedule.every().day.at("12:00"))
    def run_spider():
        fpl_spider = FPL_Spider()
        kdl_spider = KDL_Spider()
        xh_spider = XH_Spider()

        fpl_spider.run()
        kdl_spider.run()
        xh_spider.run()

    @schedule.repeat(schedule.every(10).minutes)
    def run_proxy_validation():
        validate_and_cleanup_proxies()

    

    while True:
        schedule.run_pending()
        time.sleep(1)