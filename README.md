# ProxyPool
Auto maintained personal IP pool API.

# Target 
Crawl free ip from three public ip website, stored in local Redis after data cleaning. Key-value pair in Redis will be automatically examined cycling by 10 min. Daily stable IP about 300+.</br>
## Original url:
- Free-proxy-list: [https://free-proxy-list.net/](https://free-proxy-list.net/) </br>
- Xiaohuan http: [https://ip.ihuan.me/?page=b97827cc](https://ip.ihuan.me/?page=b97827cc) </br>
- Kuaidaili: [https://www.kuaidaili.com/free/dps/](https://www.kuaidaili.com/free/dps/) </br>

# Content Including:
- Requests web crawling 
- Python-Redis
- ip proxy test/usage

# Result segments:
- ip: ipv4 ip adress with port, example: 51.161.56.52
- port: corresponding port number
- country: the ip location, example: Singapore
- https: whether the address supports https protocol
<img src="https://github.com/user-attachments/assets/da556099-3c2b-4710-a97a-c140643d38f5" width="700px" length="700px">

# Running
- Clone the source code, run start.py for auto crawl and validation through. </br>
- Proxy API: extract_ip.py/get_random_proxy(), which will return a dict of ip informations.
- Redis service is required
- A stable VPN is required for Chinese users.
- Can manually add script to run start.py upon startup.

# This project is supported by Cursor IDE
<img src="https://github.com/user-attachments/assets/16eff516-dcd6-45d6-a1b6-ba58121707cc" width="700px" length="700px">

