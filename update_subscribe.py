#!/bin/python3

'''
目标
1,从alvin9999提供的html页面，提取 ss,ssr和v2ray uri，整理成适用于 v2ray订阅;
2,从第一步和其它人的分享的v2ray订阅中，整理 ss 订阅
3,从第一步的uri中 ssr uir，整理成 适用 ssr订阅
背景
常见加密协议 shadowsocks(ss), shadowsocksR(ssr), xray(vless, vmess, torjan)

URI,对应协议。
类似网址，提供配置信息，定位到单一服务器地址，格式为"ss://, ssr://, vmess://..."

订阅 多个服务器配置集合，对应客户端。
常见订阅格式有 base64文本，(ssr, v2rayN, karing, shadowrocket)，yaml(clash),
json(ss,singbox)
注意：区分订阅传输格式和软件运行配置文件格式。比如，v2rayN 订阅b64文本，v2ray-core 
的配置是json. 另外，虽然 ss 的订阅和配置文件格式都是json,但内部的键值并不完全一样。
一般，协议作者会自己主导一个客户端，如ss,ssr,v2ray-core，这里称为官方客户端。
原生的ss和ssr客户端，都只支持各自对应协议，较为单一。且安卓ss不支持局域网共享。
ssr作者已经删库了，不再更新了。ss虽有更新，但不频频繁。
优点，占用资源少。内存，电池用量（手机端比v2ray显著节能），且感觉ssr体验更稳定。

第三方客户端，支持的协议多，兼容的平台多，功能多，如一键测速，自动更新订阅，分流。
为此，会把一些 协议的核心 core 整合到一起，且使用图形库，造成资源占用高。

采用的策略是，把 ss 和 ssr当主用, 而把v2ray当备用。

shadowsocks 订阅，有官方文档可查。
#https://shadowsocks.org/doc/sip008.html

ssr 订阅，难以查看文档。但是，在windows版本ssr程序上，自带了
一个指向github订阅网址。本身已经失效了，但是根据地址路径，搜索到github山第三方备份。
https://github.com/shadowsocksr-rm/breakwa11.github.io/blob/master/free
/freenodeplain.txt

虽然这份订阅也已不再更新。但是提供了两个信息，第一，ssr用的base文本，而非ss的json。
第二，订阅中uri格式更严格。要求必须有group。
153.125.233.236:31461:origin:aes-256-cfb:plain:bnRkdHYuY29t/?obfsparam=&
remarks=6ZmQ6YCf5biQ5Y-3IEFsdmluOTk5OQ&group=RnJlZVNTUi1wdWJsaWM

另外，ssr app 虽然支持手动导入 ss uri,但是似乎并不能正常使用，且订阅示例中，只有ssr，
没有ss,故没再深究是否支持ss订阅。

https://github.com/ssrsub/ssr
https://github.com/Alvin9999/new-pac
https://github.com/Pawdroid/Free-servers
https://github.com/ripaojiedian/freenode

github代理
https://proxy.v2gh.com/
https://gh-proxy.com/
'''
import os;
import requests;
import re;
import pytz
import base64;
import json
import uuid;
import urllib.parse
from datetime import datetime

IS_GITHUB_ACTION = bool(os.getenv("GITHUB_ACTION"));

if IS_GITHUB_ACTION:
    print("当前在Github Action环境")
    #251224新仓库链接
    url_ss_source = "https://raw.githubusercontent.com/wiki/Alvin9999-newpac/fanqiang/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7.md";
    url_v2ray_source = "https://raw.githubusercontent.com/wiki/Alvin9999-newpac/fanqiang/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7.md";
    #实测 虽然广告多，可用，速度高
    extra_source_url="https://raw.githubusercontent.com/ssrsub/ssr/master/v2ray";
else:
    print("当前不在Github Action环境")
    url_ss_source = "https://gitlab.com/zhifan999/fq/-/wikis/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7.md";
    url_v2ray_source = "https://gitlab.com/zhifan999/fq/-/wikis/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7.md";
    extra_source_url="https://proxy.v2gh.com/https://raw.githubusercontent.com/ssrsub/ssr/master/v2ray";

pattern_ss = r"ss://(?P<userinfo>[\w=+-]+)@\[?(?P<hostname>[A-Za-z0-9-:.]+)\]?:(?P<port>[A-Za-z0-9:.]+)(/\?plugin=)?(?P<plugin>[^;]+)?;?(?P<plugin_opts>[^#]+)?#(?P<tag>.+)"

#实测 uri多，但是基本都是无效
#extra_source_url = "https://proxy.v2gh.com/https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v2"

# ====== 获取当前北京时间 ======
def get_current_time():
    shanghai_tz = pytz.timezone("Asia/Shanghai")
    return datetime.now(shanghai_tz).strftime("%Y/%m/%d %H:%M:%S")

def write_to_local(file_name, content):
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(content);       

def read_from_local(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read();

#将SS-URI链接转换为在线更新要求的json格式配置
#https://shadowsocks.org/doc/sip008.html
def docode_uri2cfg(uri_ss):
    #SS-URI = "ss://" userinfo "@" hostname ":" port [ "/" ] [ "?" plugin ] [ "#" tag ]
    #userinfo = websafe-base64-encode-utf8(method  ":" password)
    #ipv6 [2001:bc8:32d7:2013::10]:1111，提取ipv6地址需注意包围[] 
    unquoted_uri = urllib.parse.unquote(uri_ss);
    #print(unquoted_uri);   
    matched = re.match(pattern_ss, unquoted_uri)
    #print(matched.group("hostname"))
    #print(matched.group("port"))    
    info_ec = matched.group("userinfo");
    while len(info_ec) % 4 != 0:
        info_ec += "=";
    info = base64.urlsafe_b64decode(
    info_ec.encode("utf-8")).decode("utf-8")   
    info_sub = info.split(":");
    uuidv4 = str(uuid.uuid4())
    #print(uuidv4)
    if  matched.group('plugin') :
        print("%s\n🔩插件 %s, %s" % (uri_ss, matched.group('plugin'), 
        matched.group('plugin_opts')))
    cfg = {\
        'id': uuidv4, \
        'remarks': urllib.parse.unquote(matched.group('tag')),\
        'server': matched.group('hostname'),\
        #为了兼容ss-rust, 这里要转换成数字，而非字符
        'server_port': int(matched.group('port')),\
        'password': info_sub[1],\
        'method': info_sub[0],\
        #如没有，则为“”， 而非null
        'plugin': matched.group('plugin') or "",\
        #测试，是上游故意 把参数这么设置，还是意外弄错 obfs-hostwwx.gxn.de5.net
        'plugin_opts': matched.group('plugin_opts') or ""\
    }    
    #print(cfg);
    return cfg
        
def add_ssr_group(ssr_url):
    content = ssr_url.replace("ssr://", "")
    while len(content) % 4 !=0:
        content += "=";
    plain_content = base64.urlsafe_b64decode(content.encode("utf-8"))\
    .decode("utf-8");    
    #根据模板，添加"group"属性
    plain_content += "&group=eXVuZmFu"; #yunfan    
    return "ssr://" + base64.urlsafe_b64encode(
    plain_content.encode("utf-8")).decode("utf-8");            

def main():
    print(f"读取指定md文档, 当前北京时间为 {get_current_time()}")
    md_ss = requests.get(url_ss_source).text;
    md_v2ray = requests.get(url_v2ray_source).text; 
    write_to_local("wiki_ss.md", md_ss);
    write_to_local("wiki_v2ray.md", md_v2ray);
    #html = read_from_local("v2ray_demo.html");
    #github
    #ss://YWVzLTI1Ni1nY206ZG9uZ3RhaXdhbmcuY29t@[2001:bc8:32d7:2013::10]:11111#SS%E8%8A%82%E7%82%B9-ipv6
    #alv_ss_ssr = re.findall(r"(ss://[A-Za-z0-9+-/=_@\[\]:#%]+|ssr://[A-Za-z0-9+/=]+)", md_ss);    
    #alv_v2_mix = re.findall(r"(vmess://[A-Za-z0-9+/=]+|vless://|hysteria2://)", md_v2ray)
    #同名称的md文件，在github中换行符号是\n ， 而在gitlab却是\r\n
    #是作者同步的同一个文件吗，还是只名称一样？ 
    pattern_uri_md = r"(?<=```bash\n)[^`\n]+(?=\n```\n)" if \
    IS_GITHUB_ACTION else r"(?<=```bash\r\n)[^`\r\n]+(?=\r\n```\r\n)";
    alv_ss_ssr = re.findall(pattern_uri_md, md_ss);
    alv_v2_mix = re.findall(pattern_uri_md, md_v2ray);        
    print(f"获得配置  ss(ssr) * {len(alv_ss_ssr)}, v2ray * {len(alv_v2_mix)}")
    #来源可靠，简单匹配
    alv_ss_iter = filter( lambda s : re.match(r"ss://", s), alv_ss_ssr)
    alv_ssr_iter = filter( lambda s : re.match(r"ssr://", s), alv_ss_ssr)
    #ssr 添加 group属性
    alv_ssr_uris = [ add_ssr_group(ssr) for ssr in alv_ssr_iter];
    #将 ss-uri 转换成 json 格式 config    
    ss_cfg_list = []
    for s in alv_ss_iter:
        ss_cfg_list.append(docode_uri2cfg(s))
    #增加更多ss uri, 数量多，但质量不高，且有的连格式都不合规，严格匹配过滤
    print(f"\n读取额外订阅，查找ss uri.")
    extra_uri_b64 = requests.get(extra_source_url).text;
    while len(extra_uri_b64) % 4 != 0:
        extra_uri_b64 += "=";
    extra_uri_plain = base64.urlsafe_b64decode(extra_uri_b64.encode("utf-8")
    ).decode("utf-8")
    extra_uri_list = extra_uri_plain.split("\n");     
    extra_ss_iter = filter(lambda s : re.match(pattern_ss, s), extra_uri_list);    
    extra_ss_list = list(extra_ss_iter);
    for s in extra_ss_iter:
        #print(s);
        ss_cfg_list.append(docode_uri2cfg(s))
    ss_json = json.dumps({'version': 1,'servers': ss_cfg_list})
    print(f"全部 ss * {len(ss_cfg_list)}") 
    
    #format
    ssr_sub = base64.urlsafe_b64encode("\n".join(alv_ssr_uris).encode(
    "utf-8")).decode("utf-8");
    #ss, ssr, v2
    v2_mix_sub = base64.urlsafe_b64encode("\n".join(alv_v2_mix + 
    alv_ss_ssr + extra_ss_list).encode("utf-8")).decode("utf-8");
    
    print(f"\n存储到文件.")
    write_to_local("ss-cfg.json", ss_json)
    write_to_local("ssr-pure.txt", ssr_sub)
    write_to_local("v2-mix.txt", v2_mix_sub)    
    print(f"更新完成, 当前北京时间为 {get_current_time()}")

if __name__ == "__main__":
    main();
