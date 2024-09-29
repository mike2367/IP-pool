# the spider for https://free-proxy-list.net/
import requests
import redis  # Add this import
from lxml import etree

class FPL_Spider:
    def __init__(self):
        self.url = "https://free-proxy-list.net/"
        self.valid_count = 0

        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)
    def get_html(self):
        response = requests.get(self.url).text
        return response

    def parse_html(self, response):
        base_xpath = '//*[@id="list"]/div/div[2]/div/table/tbody/tr'
        for tr in etree.HTML(response).xpath(base_xpath):
            try:
                item = {}
                item['ip'] = tr.xpath('./td[1]/text()')[0]
                item['port'] = tr.xpath('./td[2]/text()')[0]
                item['country'] = tr.xpath('./td[4]/text()')[0]
                item['anonymity'] = tr.xpath('./td[5]/text()')[0]
                item['https'] = tr.xpath('./td[7]/text()')[0]
                self.test_valid(item)
            except Exception as e:
                print(e)

    # check the proxy is valid
    def test_valid(self, item):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'X-Forwarded-For': f"{item['ip']}:{item['port']}"
        }
        if item['https'] == 'yes':  
            proxies = {
                "https": f"{item['ip']}:{item['port']}"
            }
        else:
            proxies = {
                "http": f"{item['ip']}:{item['port']}",
            }       
        if item['anonymity'] == 'elite proxy':
            try:
                response = requests.get("https://httpbin.org/ip", proxies=proxies, headers=headers, timeout=2).json()
                if response.get('origin').split(",")[0] == f"{item['ip']}:{item['port']}":
                    print("success")
                    # Store in Redis
                    if not self.redis_client.exists(f"{item['ip']}:{item['port']}"):
                        self.redis_client.hset(f"{item['ip']}:{item['port']}", mapping={
                            'country': item['country'],
                            'https': item['https']  
                        })
                        self.valid_count += 1
                else:
                    print(f"Proxy {item['ip']}:{item['port']} is not valid")
                    print(response.get('origin').split(",")[0])
                    raise Exception('proxy is not valid')

            except Exception as e:
                print(e)

    def run(self):
        html = self.get_html()
        self.parse_html(html)
        print(f"Valid proxies: {self.valid_count}")

# if __name__ == "__main__":
#     spider = FPL_Spider()
#     spider.run()