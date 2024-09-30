# the spider for https://www.kuaidaili.com/free/inha
# all the proxies are from mainland China, HTTP only
import requests
import redis  # Redis is used for storing valid proxies
from lxml import etree
import random
from Useragents import ua_list
import json
import time
class KDL_Spider:
    def __init__(self):
        self.url = "https://www.kuaidaili.com/free/inha/"
        self.valid_count = 0

        # Initialize Redis client
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)

    def get_html(self, url):
        headers = {
            'User-Agent': random.choice(ua_list),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.kuaidaili.com/free/inha/',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Forwarded-For': '117.136.104.106',
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching HTML: {e}")
            return ""

    def parse_html(self, response):

        item = {}
        html = response
        info_list = html[html.find('const fpsList = ') + len('const fpsList = '):html.find('}];')] + '}]'
        info_list = json.loads(info_list)
        for info in info_list:
            item['ip'] = info.get('ip')
            item['port'] = info.get('port')
            item['location'] = info.get('location')
            self.test_valid(item)

    # Check if the proxy is valid
    def test_valid(self, item):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'X-Forwarded-For': f"{item['ip']}:{item['port']}"
        }

        proxies = {
                "http": f"http://{item['ip']}:{item['port']}",
        }

        try:
            response = requests.get(
                "https://httpbin.org/ip",
                    proxies=proxies,
                    headers=headers,
                    timeout=2
                )
            response.raise_for_status()
            origin = response.json().get('origin', '')
            if origin.split(",")[0].strip() == f"{item['ip']}:{item['port']}":
                
                # Store in Redis if not already present
                proxy_key = f"{item['ip']}:{item['port']}"
                if not self.redis_client.exists(proxy_key):
                    self.redis_client.hset(proxy_key, mapping={
                            'country': "China-" + item['location'],
                            'https': "no"
                        })
                    print(f"Success: {item['ip']}:{item['port']}")
                    self.valid_count += 1
                else:
                    print(f"Duplicate proxy {item['ip']}:{item['port']}")
            else:
                print(f"Invalid proxy {item['ip']}:{item['port']}")
        except requests.RequestException as e:
            print(f"Request error with proxy {item['ip']}:{item['port']}: {e}")
        except ValueError as e:
            print(f"JSON decode error with proxy {item['ip']}:{item['port']}: {e}")
        except Exception as e:
            print(f"Unexpected error with proxy {item['ip']}:{item['port']}: {e}")

    def run(self):
        for i in range(1,10):
            url = self.url.format(i)
            html = self.get_html(url)
            self.parse_html(html)
            time.sleep(random.randint(1, 3))
        print(f"Valid proxies found: {self.valid_count}")

# To execute the spider, uncomment the following lines:
if __name__ == "__main__":
    spider = KDL_Spider()
    spider.run()