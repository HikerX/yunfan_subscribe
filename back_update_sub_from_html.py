#!/usr/bin/python3

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

import requests;
import re;
import base64;
import json
import uuid;
import urllib.parse

#https://raw.githubusercontent.com/wiki/Alvin9999/new-pac/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7.md
#https://raw.githubusercontent.com/wiki/Alvin9999/new-pac/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7.md
ss_url_github = "https://github.com/Alvin9999/new-pac/wiki/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7";
v2ray_url_github = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7";
#url = "https://gitlab.com/zhifan999/fq/-/wikis/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"
#url = "https://s3.dualstack.us-west-2.amazonaws.com/zhifan2/wiki.html"

#实测 uri多，但是基本都是无效
#ssv2_url_fn = "https://proxy.v2gh.com/https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v2"
#实测 虽然广告多，可用，速度高
ssv2_url_fn="https://raw.githubusercontent.com/ssrsub/ssr/master/v2ray";

def write_to_local(file_name, content):
    f = open(file_name, "w");
    f.write(content)
    f.close();

#write_to_local("v2ray_demo.html", html);

def read_from_local(file_name):
    f = open(file_name, "r");
    return f.read();


#将SS-URI链接转换为在线更新要求的json格式配置
#https://shadowsocks.org/doc/sip008.html
def trans_uri2cfg(ss_uri):
	#SS-URI = "ss://" userinfo "@" hostname ":" port [ "/" ] [ "?" plugin ] [ "#" tag ]
	#userinfo = websafe-base64-encode-utf8(method  ":" password)
	#           method ":" password 
	# hostname ipv4 111.22.22.33:2345, 
	#ipv6 [2001:bc8:32d7:2013::10]:1111，提取ipv6地址需注意包围[]
	mPattern = r"ss://(?P<userinfo>[\w=+-]+)@\[?(?P<hostname>[A-Za-z0-9:.]+)\]?:(?P<port>[A-Za-z0-9:.]+)#(?P<tag>.+)"
	matched = re.search(mPattern, ss_uri)
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
	
	cfg = {'id': uuidv4, \
	'remarks': urllib.parse.unquote(matched.group('tag')),\
	'server': matched.group('hostname'),\
	#为了兼容ss-rust, 这里要转换成数字，而非字符
	'server_port': int(matched.group('port')),\
	'password': info_sub[1],\
	'method': info_sub[0],\
	'plugin': '',\
	'plugin_opts': ''}    
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

    ss_html = requests.get(ss_url_github).text;
    v2ray_html = requests.get(v2ray_url_github).text;
    #print(html)

    fn_uri_ec = requests.get(ssv2_url_fn).text;
    
    #write_to_local("freenodes-uri.txt", fn_uri_ec)
    
    while len(fn_uri_ec) % 4 != 0:
        fn_uri_ec += "=";
    fn_ss_text = base64.urlsafe_b64decode(
    fn_uri_ec.encode("utf-8")).decode("utf-8")

    fn_ss_list = fn_ss_text.split("\n");
    fn_ss_iter = filter(lambda s : re.match("ss://", s), fn_ss_list)

    #html = read_from_local("v2ray_demo.html");

    #github
    alv_ss_ssr = re.findall(r"data-snippet-clipboard-copy-content=\"([^\"]+)\"", ss_html);
    alv_v2_mix = re.findall(r"data-snippet-clipboard-copy-content=\"([^\"]+)\"", v2ray_html);

    #gitlab
    #v2ray_urls = re.findall(r"```bash\\r\\n([^`]+)\\r\\n```", html);

    #sub_urls = ssr_urls;

    #v2 从html页面提取，替换"&amp;"符号为"&"
    for url in alv_v2_mix:
        #上游已经修复 缺少 vmess前缀的格式错误
        '''
        if not re.match(r"vless|vmess|hysteria", url):
            url = f"vmess://{url}"
        '''
        if not re.match("&amp;", url):
            url = url.replace("&amp;", "&");
        #sub_urls.append(url)

    
    #finding pure ssr , filter
    alv_ss_uris = filter( lambda s : re.match(r"ss://", s), alv_ss_ssr)
    alv_ssr_uris = filter( lambda s : re.match(r"ssr://", s), alv_ss_ssr)
    
    #ssr 添加 group属性
    alv_ssr_uris = [ add_ssr_group(ssr) for ssr in alv_ssr_uris]

    #ss_urls = filter ( lambda url : re.match("ss://", url) ,  ssr_urls )
    
    #将 ss-uri 转换成 json 格式 config    
    ss_cfg_list = []
    for s in alv_ss_uris:
        ss_cfg_list.append(trans_uri2cfg(s))    
        
    for s in fn_ss_iter:
        ss_cfg_list.append(trans_uri2cfg(s))
    cfg_json = json.dumps({'version': 1,'servers': ss_cfg_list})

    #format
    #sub_urls = [u.replace("&amp;", "&")  for u in urls ]
    #print(sub_urls)
    #ss_pure_sub = base64.b64encode("\n".join(alv_ss_uris).encode("utf-8")).decode("utf-8");
    ssr_sub = base64.urlsafe_b64encode("\n".join(alv_ssr_uris)\
    .encode("utf-8")).decode("utf-8");
    #ss, ssr, v2
    v2_mix_sub = base64.urlsafe_b64encode("\n".join(alv_ss_ssr + 
    alv_v2_mix).encode("utf-8")).decode("utf-8");

    print(f"{len(ss_cfg_list)} ss cfg, {len(alv_ssr_uris)} ssr,\
    {len(alv_v2_mix)} v2ray")    
    write_to_local("ss-cfg.json", cfg_json)
    write_to_local("ssr-pure.txt", ssr_sub)

    write_to_local("v2-mix.txt", v2_mix_sub)

if __name__ == "__main__":
    main();
