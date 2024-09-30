# the spider for https://free-proxy-list.net/
import requests
import redis
import random
from lxml import etree
from Useragents import ua_list


class FPL_Spider:
    def __init__(self):
        self.url = "https://free-proxy-list.net/"
        self.valid_count = 0

        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)

    def get_html(self):
        headers = {
            'User-Agent': random.choice(ua_list),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
        try:
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching HTML: {e}")
            return ""

    def parse_html(self, response):
        base_xpath = '//*[@id="list"]/div/div[2]/div/table/tbody/tr'
        for tr in etree.HTML(response).xpath(base_xpath):
            try:
                item = {}
                item['ip'] = tr.xpath('./td[1]/text()')[0].strip()
                item['port'] = tr.xpath('./td[2]/text()')[0].strip()
                item['country'] = tr.xpath('./td[4]/text()')[0].strip()
                item['anonymity'] = tr.xpath('./td[5]/text()')[0].strip()
                item['https'] = tr.xpath('./td[7]/text()')[0].strip().lower()
                self.test_valid(item)
            except Exception as e:
                print(f"Error parsing row: {e}")

    def test_valid(self, item):
        headers = {
            'User-Agent': random.choice(ua_list),
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
        if item['anonymity'].lower() == 'elite proxy':
            try:
                response = requests.get("https://httpbin.org/ip", proxies=proxies, headers=headers, timeout=5)
                response.raise_for_status()
                origin = response.json().get('origin', '')
                if origin.split(",")[0].strip() == f"{item['ip']}:{item['port']}":
                    # Store in Redis if not already present
                    proxy_key = f"{item['ip']}:{item['port']}"
                    if not self.redis_client.exists(proxy_key):
                        self.redis_client.hset(proxy_key, mapping={
                            'country': item['country'],
                            'https': item['https']
                        })
                        print(f"Success: {proxy_key}")
                        self.valid_count += 1
                    else:
                        print(f"Duplicate proxy {proxy_key}")
                else:
                    print(f"Invalid proxy {item['ip']}:{item['port']}")
            except requests.RequestException as e:
                print(f"Request error with proxy {item['ip']}:{item['port']}: {e}")
            except ValueError as e:
                print(f"JSON decode error with proxy {item['ip']}:{item['port']}: {e}")
            except Exception as e:
                print(f"Unexpected error with proxy {item['ip']}:{item['port']}: {e}")

    def run(self):
        html = self.get_html()
        if html:
            self.parse_html(html)
        print(f"Valid proxies: {self.valid_count}")

# if __name__ == "__main__":
#     spider = FPL_Spider()
#     spider.run()