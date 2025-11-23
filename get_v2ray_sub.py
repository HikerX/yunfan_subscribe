import requests;
import re;
import base64;

v2ray_url_github = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7";

ss_url_github = "https://github.com/Alvin9999/new-pac/wiki/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7";

#url = "https://gitlab.com/zhifan999/fq/-/wikis/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"

#url = "https://s3.dualstack.us-west-2.amazonaws.com/zhifan2/wiki.html"

#url = "https://www.baidu.com"

v2ray_html = requests.get(v2ray_url_github).text;

ss_html = requests.get(ss_url_github).text;

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
v2ray_urls = re.findall(r"data-snippet-clipboard-copy-content=\"([^\"]+)\"", v2ray_html);

#gitlab
#v2ray_urls = re.findall(r"```bash\\r\\n([^`]+)\\r\\n```", html);

sub_urls = [];
for url in v2ray_urls:
    if not re.match(r"vless|vmess|hysteria", url):
        url = f"vmess://{url}"
    elif not re.match("&amp;", url):
        url = url.replace("&amp;", "&");
    sub_urls.append(url)

ss_ssr_urls = re.findall(r"data-snippet-clipboard-copy-content=\"([^\"]+)\"", ss_html);
#ss_urls = filter ( lambda url : re.match("ss://", url) ,  ss_ssr_urls )

print(f"{len(v2ray_urls)} v2ray_url, {len(ss_ssr_urls)} ss_ssr_urls")

#format
#sub_urls = [u.replace("&amp;", "&")  for u in urls ]
sub_urls.extend(ss_ssr_urls);
#print(sub_urls)

subContent = base64.b64encode("\n".join(sub_urls).encode("utf-8")).decode("utf-8");
write_to_local("v2ray_sub", subContent)
print("succeed")
