import redis
import random
 
"""
Randomly selects an IP from the Redis database and returns it.
"""
def get_random_proxy():

    redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)
    proxy_keys = redis_client.keys('*:*')
    
    if not proxy_keys:
        print("No proxies available")
        return None
    
    random_key = random.choice(proxy_keys).decode()
    ip, port = random_key.split(':')
    
    proxy_info = redis_client.hgetall(random_key)
    
    try:
        country = proxy_info[b'country'].decode()
    except KeyError:
        print(f"Proxy {ip}:{port} is missing the 'country' field.")
        redis_client.delete(random_key)
        return None  
    
    try:
        https = proxy_info[b'https'].decode().lower()
    except KeyError:
        print(f"Proxy {ip}:{port} is missing the 'https' field.")
        redis_client.delete(random_key)
        return None  
    
    return {
        'ip': ip,
        'port': port,
        'country': country,
        'https': https
    }

# if __name__ == "__main__":
#     proxy = get_random_proxy()
#     if proxy:
#         https_status = proxy['https'].capitalize()
#         print(f"Random proxy: {proxy['ip']}:{proxy['port']} | Country: {proxy['country']} | HTTPS: {https_status}")

