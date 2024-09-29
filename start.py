from .spiders.free_proxy_list import FPL_Spider
from .redis_check.ip_validate import validate_and_cleanup_proxies

if __name__ == "__main__":  
    spider = FPL_Spider()
    spider.run()