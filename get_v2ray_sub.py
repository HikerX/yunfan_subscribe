import requests;
import re;
import base64;

v2ray_url_github = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7";

ssr_url_github = "https://github.com/Alvin9999/new-pac/wiki/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7";

#url = "https://gitlab.com/zhifan999/fq/-/wikis/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"

#url = "https://s3.dualstack.us-west-2.amazonaws.com/zhifan2/wiki.html"

#url = "https://www.baidu.com"

ssr_html = requests.get(ssr_url_github).text;

v2ray_html = requests.get(v2ray_url_github).text;

#print(html)

def write_to_local(file_name, content):
    f = open(file_name, "w");
    f.write(content)
    f.close();

#write_to_local("v2ray_demo.html", html);

def read_from_local(file_name):
    f = open(file_name, "r");
    return f.read();

#html = read_from_local("v2ray_demo.html");

#github
ssr_urls = re.findall(r"data-snippet-clipboard-copy-content=\"([^\"]+)\"", ssr_html);
v2ray_urls = re.findall(r"data-snippet-clipboard-copy-content=\"([^\"]+)\"", v2ray_html);

#gitlab
#v2ray_urls = re.findall(r"```bash\\r\\n([^`]+)\\r\\n```", html);

#sub_urls = ssr_urls;

#fix missing vmess protocal prefix
for url in v2ray_urls:
    #上游已经修复 缺少 vmess前缀的格式错误
    '''
    if not re.match(r"vless|vmess|hysteria", url):
        url = f"vmess://{url}"
    '''
    if not re.match("&amp;", url):
        url = url.replace("&amp;", "&");
    #sub_urls.append(url)

#ss_urls = filter ( lambda url : re.match("ss://", url) ,  ssr_urls )

print(f"{len(v2ray_urls)} v2ray_url, {len(ssr_urls)} ssr_urls")

#format
#sub_urls = [u.replace("&amp;", "&")  for u in urls ]
#print(sub_urls)
#ss+ssr
ssrSubContent = base64.b64encode("\n".join(ssr_urls).encode("utf-8")).decode("utf-8");
#ss+v2
v2SubContent = base64.b64encode("\n".join(ssr_urls + v2ray_urls)\
.encode("utf-8")).decode("utf-8");
write_to_local("ssr_sub", ssrSubContent)
write_to_local("v2ray_sub", v2SubContent)
print("succeed")
