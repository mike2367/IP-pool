from .spiders.free_proxy_list import FPL_Spider
from .redis_check.ip_validate import validate_and_cleanup_proxies

if __name__ == "__main__":  
    import schedule
    import time

    def run_spider():
        spider = FPL_Spider()
        spider.run()

    schedule.every().day.at("12:00").do(run_spider)
    schedule.every(10).minutes.do(validate_and_cleanup_proxies)

    while True:
        schedule.run_pending()
        time.sleep(1)