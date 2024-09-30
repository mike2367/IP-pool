import requests
import redis
import random
import time
from lxml import etree
from Useragents import ua_list


class XH_Spider:
    def __init__(self):
        self.url = "https://ip.ihuan.me/anonymity/2.html{}"
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
            'Referer': 'https://ip.ihuan.me/',
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

        next_page_url = etree.HTML(response).xpath('//ul[@class="pagination"]/li[8]/a/@href')
        if next_page_url:
            next_page_url = next_page_url[0]
        else:
            return None
        item = {}
        html = response
        soup = etree.HTML(html)
        proxy_list = soup.xpath('/html/body//div[2]/div[2]/table/tbody/tr')
        for proxy in proxy_list:
            item['ip'] = proxy.xpath('.//td[1]/a/text()')[0]
            item['port'] = proxy.xpath('.//td[2]/text()')[0]
            item['location'] = proxy.xpath('.//td[3]/a/text()')[0]
            # Assuming there is a column indicating https
            https = proxy.xpath('.//td[5]/text()')[0]
            item['https'] = 'yes' if https == '支持' else 'no'
            self.test_valid(item)
        
        return next_page_url


    # Check if the proxy is valid
    def test_valid(self, item):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'X-Forwarded-For': f"{item['ip']}:{item['port']}"
        }

        if item['https'] == 'yes':
            proxies = {
                "https": f"https://{item['ip']}:{item['port']}"
            }
        else:
            proxies = {
                "http": f"http://{item['ip']}:{item['port']}"
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
                        'country': item['location'],
                        'https': item['https']
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
        # take 5 pages daily
        page_count = 0

        html = self.get_html(self.url.format("?page=b97827cc"))
        next_page_url = self.parse_html(html)
        while page_count < 5:
            html = self.get_html(self.url.format(next_page_url))
            next_page_url = self.parse_html(html)
            if next_page_url is None:
                break
            time.sleep(random.randint(1, 3))
            page_count += 1
# To execute the spider, uncomment the following lines:
# if __name__ == "__main__":
#     spider = XH_Spider()
#     spider.run()
