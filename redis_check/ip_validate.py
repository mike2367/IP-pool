import requests
import redis

def validate_and_cleanup_proxies():
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)
    proxy_keys = redis_client.keys('*:*')

    for key in proxy_keys:
        proxy_key = key.decode()
        ip, port = proxy_key.split(':')
        https = redis_client.hget(proxy_key, 'https').decode()

        if https.lower() == 'yes':
            proxies = {
                "https": f"https://{ip}:{port}"
            }
        else:
            proxies = {
                "http": f"http://{ip}:{port}"
            }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'X-Forwarded-For': f"{ip}:{port}"
        }

        try:
            response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=2, headers=headers).json()
            if not response.get('origin').split(",")[0] == f"{ip}:{port}":
                raise Exception('proxy is not valid')
        except Exception as e:
            redis_client.delete(proxy_key)
            print(f"Deleted invalid proxy: {ip}:{port}")
    
    print("All proxies up to date")

# if __name__ == "__main__":
#     validate_and_cleanup_proxies()
