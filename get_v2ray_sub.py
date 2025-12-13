import requests;
import re;
import base64;

ss_url_github = "https://github.com/Alvin9999/new-pac/wiki/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7";
v2ray_url_github = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7";
#url = "https://gitlab.com/zhifan999/fq/-/wikis/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"
#url = "https://s3.dualstack.us-west-2.amazonaws.com/zhifan2/wiki.html"

ss_html = requests.get(ss_url_github).text;
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
ss_ssr_urls = re.findall(r"data-snippet-clipboard-copy-content=\"([^\"]+)\"", ss_html);
v2_mix_urls = re.findall(r"data-snippet-clipboard-copy-content=\"([^\"]+)\"", v2ray_html);

#gitlab
#v2ray_urls = re.findall(r"```bash\\r\\n([^`]+)\\r\\n```", html);

#sub_urls = ssr_urls;

#finding pure ssr , filter
ss_pure_urls = filter( lambda s : re.match(r"ss://", s), ss_ssr_urls)
ssr_pure_urls = filter( lambda s : re.match(r"ssr://", s), ss_ssr_urls)

def add_ssr_group(ssr_url):
    content = ssr_url.replace("ssr://", "")
    while len(content) % 4 !=0:
        content += "=";
    plain_content = base64.urlsafe_b64decode(content.encode("utf-8"))\
    .decode("utf-8");    
    #根据模板，添加"group"属性
    plain_content += "&group=eXVuZmFu"; #yunfan    
    return "ssr://" + base64.urlsafe_b64encode(plain_content.encode("utf-8")).decode("utf-8");    

ssr_pure_urls = [ add_ssr_group(ssr) for ssr in ssr_pure_urls]

#fix missing vmess protocal prefix
for url in v2_mix_urls:
    #上游已经修复 缺少 vmess前缀的格式错误
    '''
    if not re.match(r"vless|vmess|hysteria", url):
        url = f"vmess://{url}"
    '''
    if not re.match("&amp;", url):
        url = url.replace("&amp;", "&");
    #sub_urls.append(url)

#ss_urls = filter ( lambda url : re.match("ss://", url) ,  ssr_urls )

print(f"{len(v2_mix_urls)} v2ray_url, {len(ss_ssr_urls)} ssr_urls")

#format
#sub_urls = [u.replace("&amp;", "&")  for u in urls ]
#print(sub_urls)
ss_pure_sub = base64.b64encode("\n".join(ss_pure_urls).encode("utf-8")).decode("utf-8");
ssr_pure_sub = base64.b64encode("\n".join(ssr_pure_urls).encode("utf-8")).decode("utf-8");
#ss+ssr 
ss_ssr_sub = base64.b64encode("\n".join(ss_ssr_urls).encode("utf-8")).decode("utf-8");
#ss, ssr, v2
v2_mix_sub = base64.b64encode("\n".join(ss_ssr_urls + v2_mix_urls)\
.encode("utf-8")).decode("utf-8");
write_to_local("ss-pure.txt", ss_pure_sub)
write_to_local("ssr-pure.txt", ssr_pure_sub)
write_to_local("ss-ssr.txt", ss_ssr_sub)
write_to_local("v2-mix.txt", v2_mix_sub)

