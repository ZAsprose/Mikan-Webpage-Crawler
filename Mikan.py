import sys
import os
import shutil
import requests
from lxml import etree
from fake_useragent import UserAgent
from scrapingbee import ScrapingBeeClient

from concurrent.futures import ThreadPoolExecutor
import threading
import time
import math

import PySimpleGUI as sg

class Mikan:

    def __init__(self):
        self.url = "https://mikanani.me"
        self.ua = UserAgent()
        self.ifproxy = False
        self.bangumilist = "bangumilist.txt"
        self.searchlist = "searchlist.txt"
        self.proxylist = "proxylist.txt"
        self.workingproxies = "workingproxies"
        self.proxylink = ""
        self.iftorrent = False
        self.ifmagnet = True
        self.proxies = {
            "https": "0.0.0.0:80"
        }

        if os.path.exists('result'):
            shutil.rmtree('result')           
        if not os.path.exists(self.bangumilist):
            f = open(self.bangumilist, "w")
            f.close()
        if not os.path.exists(self.searchlist):
            f = open(self.searchlist, "w")
            f.close()
    
    """
    generate fake header
    """
    def header_generate(self):
        self.headers = {
            'User-Agent': self.ua.random,
        }

    """
    get page html using requests
    """
    def raw_get_page(self, url):
        res = requests.get(url=url, headers=self.headers)
        html = res.content
        # print(html)
        return html.decode("utf-8")

    """
    get page html using proxy
    """
    def proxy_get_page(self, url):     
        res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        html = res.content
        return html.decode("utf-8")

    def get_page(self, url):
        if self.ifproxy:
            return self.proxy_get_page(url)
        else:
            return self.raw_get_page(url)

    """
    form file name and create it, under folder result
    """
    def form_res_file(self, title):
        if not os.path.exists('result'):
            os.makedirs('result')
        fn = "result/" + title + ".txt"
        f = open(fn, "w")
        f.close()
        return fn

    """
    form url in different situation
    """
    def format_url_to_start(self, category, param):
        real_url = ""
        if category == "search":
            real_url = self.url + "/Home/Search?searchstr="
        elif category == "classic":
            real_url = self.url + "/Home/Classic/"
        elif category == "episode" or category == "detail":
            real_url = self.url
        elif category == "bangumi":
            real_url = self.url + "/Home/Bangumi/"
        else:
            return real_url
        
        real_url += param
        return real_url.format(1)

    """
    write name of cartoon, torrent link(optional), magnet link(optional) to the file
    """
    def write_result_to_file(self, filename, title, torrent, magnet):
        with open(filename, "a", encoding="utf-8") as f:
                f.write(title + '\n')
                if self.iftorrent:
                    f.write(torrent + '\n')
                if self.ifmagnet:
                    f.write(magnet + '\n')
                f.write('\n')

    """
    get download information from detail page html from classic page html
    """
    def get_detail_page_from_classic(self, filename, html):
        parse_html = etree.HTML(html)
        one = parse_html.xpath('//tbody//tr//td[3]/a/@href')
        # print(len(one))
        # li = one[0]
        for li in one:
            # yr = "https://mikanani.me" + li
            yr = self.format_url_to_start("detail", li)
            # print(yr)
            html2 = self.get_page(yr)
            self.parse_detail_page(filename, html2)       
    
    """
    get download information from bangumi page html coming from search result html
    """
    def get_episode_page(self, html):
        # print(html.encode("utf-8"))
        parse_html = etree.HTML(html)
        episodes = parse_html.xpath('//ul/li/a/div[@class="an-info"]/..')
        # print(len(episodes))
        for i in episodes:            
            title = i.xpath('./div/div/div[@class="an-text"]/text()')
            # print(len(title))
            x = self.form_res_file(title[0].strip())
            # h = "https://mikanani.me" + i.xpath('@href')[0].strip()
            h = self.format_url_to_start("episode", i.xpath('@href')[0].strip())
            print(h)            
            html2 = self.get_page(h)
            self.parse_episode_page(x, html2)

    """
    generate bangumi-mikanId pair from search result and write them down to bangumi list
    """
    def generate_bangumi_list_from_search(self, html):
        parse_html = etree.HTML(html)
        episodes = parse_html.xpath('//ul/li/a/div[@class="an-info"]/..')
        for i in episodes:            
            title = i.xpath('./div/div/div[@class="an-text"]/text()')[0].strip()                      
            h = self.format_url_to_start("episode", i.xpath('@href')[0].strip())
            num = h.split("/").pop()            
            with open(self.bangumilist, "a", encoding="utf-8") as f:
                f.write(title + '<->')
                f.write(num + '\n')            
    
    """
    get download information from one bangumi page html and write them down to file
    """          
    def parse_episode_page(self, filename, html):
        parse_html = etree.HTML(html)
        tr = parse_html.xpath('//tbody/tr/td/a[@class="magnet-link-wrap"]/../..')
        # i = tr[0]
        for i in tr:
            magnet = i.xpath('./td/a[2]/@data-clipboard-text')
            torrent = self.url + i.xpath('./td[4]/a/@href')[0].strip()
            # print(len(magnet))
            title = i.xpath('./td/a[@class="magnet-link-wrap"]/text()')
            # print(len(title))
            self.write_result_to_file(filename, title[0].strip(), torrent, magnet[0].strip())

    """
    get download information from one detail page html and write them down to file
    """
    def parse_detail_page(self, filename, html):
        parse_html = etree.HTML(html)
        tow = parse_html.xpath('//body') 
        # print(len(tow))           
        for i in tow:
            four = i.xpath('//p[@class="episode-title"]//text()')
            # print(len(four))
            four = four[0].strip()
            torrent = self.url + i.xpath('.//div[@class="leftbar-nav"]/a[1]/@href')[0].strip()
            magnet = i.xpath('.//div[@class="leftbar-nav"]/a[2]/@href')[0].strip()
            # # print(torrent)
            # print(magnet)
            self.write_result_to_file(filename, four, torrent, magnet)
    
    """
    generate download information file via detail pages links from classic page
    """    
    def get_torrent_and_magnet_from_classic_page(self, param):
        self.header_generate()        
        filename = self.form_res_file("list_p" + param)
        link = self.format_url_to_start("classic", param)        
        html = self.get_page(link) 
        self.get_detail_page_from_classic(filename, html)

    """
    get episode pages from search result
    """
    def get_from_episode_page_by_search(self, param):
        self.header_generate()
        link = self.format_url_to_start("search", param)
        html = self.get_page(link) 
        self.get_episode_page(html)

    """
    generate download information file from a bangumi page
    """
    def get_magnet_from_episode_page_by_bangumi(self, title, param):
        self.header_generate()
        link = self.format_url_to_start("bangumi", param)
        print(link)
        fn = self.form_res_file(title)        
        html = self.get_page(link) 
        self.parse_episode_page(fn, html)
    
    """
    generate bangumi list file by one search result
    """    
    def get_bangumilist_from_search(self, param):
        self.header_generate()
        link = self.format_url_to_start("search", param)
        html = self.get_page(link) 
        self.generate_bangumi_list_from_search(html)
    """
    generate download information file from a search result page
    """
    def get_magnet_by_search(self, param):
        self.header_generate()
        link = self.format_url_to_start("search", param)
        # print(link)
        fn = self.form_res_file("search_" + param)
        # print(fn)
        html = self.get_page(link)
        # print(html.encode("utf-8"))
        self.parse_episode_page(fn, html)

    """
    generate download information files from search results of search list
    """
    def get_magnet_from_searchlist(self):
        with open(self.searchlist, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            self.get_magnet_by_search(line.strip())

    """
    generate download information files for bangumis on bangumi list
    """
    def get_magnet_from_episode_by_bangumilist(self):
        with open(self.bangumilist, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            arr = line.split("<->")
            self.get_magnet_from_episode_page_by_bangumi(arr[0].strip(), arr[1].strip())

    """
    generate bangumi list based on search results of search list
    """
    def generate_bangumilist_from_searchlist(self):        
        with open(self.searchlist, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            self.get_bangumilist_from_search(line.strip())
    """
    test if proxy can work
    """
    def test_proxy(self, proxy):
        self.header_generate()
        self.proxies = {
            "https": proxy
        }
        # print(self.proxies)
        status = 0
        try:
            res = requests.get(url="https://mikanani.me/Home/Classic", headers=self.headers, proxies=self.proxies)
            status = res.status_code
        finally:
            if status == 200:
                return True
            else:
                return False

    """
    get proxy file from link
    """
    def save_proxy_list(self):
        if os.path.exists(self.proxylist):
            os.remove(self.proxylist)
        r = requests.get(self.proxylink, allow_redirects=True)
        open(self.proxylist, 'wb').write(r.content)

    """
    test if proxy in proxy list works one by one
    """
    def test_proxies(self, proxies):
        filepath = self.workingproxies + "/f_" + str(proxies[0]) + ".txt"
        # print(threading.current_thread().name + '  ' + str(filepath) + '\n') 
        buff = []
        for proxy in proxies[1]:
            # print(threading.current_thread().name + '  ' + proxy.strip())
            if self.test_proxy(proxy.strip()): 
                buff.append(proxy)
        # print(threading.current_thread().name + ' res: ' + str(len(buff)) + '\n') 
        if len(buff) > 0:
            if not os.path.exists(filepath):
                f = open(filepath, "w")
                f.close()
            # print(threading.current_thread().name + ' ' + str(buff) + '\n') 
            with open(filepath, "a", encoding="utf-8") as f:                 
                for i in buff:
                    f.write(i)


    """
    get a list of working proxy from proxylist file and write to file
    """
    def get_working_proxies(self, threads):        
        if os.path.exists(self.workingproxies):
            shutil.rmtree(self.workingproxies)  
        os.makedirs(self.workingproxies)            
        
        with open(self.proxylist, "r", encoding="utf-8") as f:
            lines = f.readlines()
        lines = lines[0: 1000]
        upperbound = math.ceil(len(lines)/10)

        buff = []
        for i in range(0, upperbound):          
            proxies = lines[i*10: (i+1)*10]
            buff.append([i, proxies])

        with ThreadPoolExecutor(max_workers=threads) as pool:            
            results = pool.map(self.test_proxies, buff)
            print('\n--------------\n')
            for r in results:
                # print(r)
                r

        print("proxy work done")

    """
    generate workingproxies.txt based on workingproxies folder
    """
    def generate_workingproxies_file(self):
        print("start to generate workingproxies file")
        buff = []
        fs = os.listdir(self.workingproxies + '/')
        # print(fs)
        for f in fs:
            buff = buff + open(self.workingproxies + '/' + f, 'r', encoding="utf-8").readlines()

        buff = buff[::-1]
        print(buff)
        if len(f) > 0:
            wpf = self.workingproxies + '.txt'
            if os.path.exists(wpf):
                os.remove(wpf)
            if not os.path.exists(wpf):
                f = open(wpf, "w")
                f.close()
            
            with open(wpf, "a", encoding="utf-8") as f:                 
                for i in buff:
                    f.write(i.strip() + '\n')
            return True
        else:
            return False   
    
    """
    entrance of get migan
    """
    def get_migan(self, classic_page_range = 0, ifsearch = False, ifbangumi = False, ifSerToBan = False):
        if ifSerToBan:
            self.generate_bangumilist_from_searchlist()
        if ifsearch:
            self.get_magnet_from_searchlist()
        if ifbangumi:
            self.get_magnet_from_episode_by_bangumilist()        

        for i in range(1, classic_page_range+1):
            self.get_torrent_and_magnet_from_classic_page(str(i))

    """
    entrance of the whole process
    """
    def start_migan(self, classic_page_range = 0, ifsearch = False, ifbangumi = False, ifSerToBan = False, proxy = False, 
        ifdownloadfromurl = False, threads = 10,
        iftorrent = False, ifmagnet = True, 
        searchlist = "searchlist.txt", bangumilist = "bangumilist.txt", 
        workingproxies = "workingproxies", 
        proxylink = ""):       
        self.ifproxy = proxy
        self.bangumilist = bangumilist
        self.searchlist = searchlist
        self.iftorrent = iftorrent
        self.ifmagnet = ifmagnet
        self.workingproxies = workingproxies
        self.proxylink = proxylink
        lines = []        
        
        ifcanproxy = False
        if self.ifproxy:
            if not ifdownloadfromurl:
                ifcanproxy = True
            else:
                self.save_proxy_list()
                self.get_working_proxies(threads)
                ifcanproxy = self.generate_workingproxies_file()
            # 
            if not ifcanproxy:
                sys.exit("No valid proxy from the proxy link")
            else:
                proxies = []
                with open(self.workingproxies + ".txt", "r", encoding="utf-8") as f:
                    proxies = f.readlines()
                for proxy in proxies:
                    print(proxy)
                    proxy = proxy.strip()
                    res = self.test_proxy(proxy)
                    print(res)

                    ifsuccess = False
                    if res:
                        self.proxies = {
                            "https": proxy
                        }
                        try:
                            self.get_migan(classic_page_range, ifsearch, ifbangumi, ifSerToBan)
                            print("using proxy: " + proxy + " success~")
                            ifsuccess = True                            
                        except:
                            print("using proxy: " + proxy + " fail!")
                            continue
                    else:
                        continue 
                    break                  
        else:
            self.get_migan(classic_page_range, ifsearch, ifbangumi, ifSerToBan)
                
        print("Done")      

proxy = True
ifcanproxy = False
classic_page_range = 0
threads = 10
bangumilist = "bangumilist.txt"
searchlist = "searchlist.txt"
workingproxies = "workingproxies"
proxylink = ""

proxySection = [ 
        [sg.Checkbox("Get proxy list downloaded from URL and verify them:", key = "downloadFromURL", default = True, enable_events = True, size = (50, 1))],
        [sg.Input(proxylink, size = (68, 1), key = "proxylink")],
        [sg.Text("ADVANCED: Number of threads for proxy check: "), sg.Push(), 
        sg.Input(threads, size = (20,1), key = "threads")],
        [sg.Text("Load working proxy from file: "), sg.Push(),
        sg.Input(workingproxies, size = (20, 1), key = "workingproxies", disabled = True)],
        [sg.Text("\t\t*.txt, only input file name such as 'workingproxies'", size = (60, 1))]
    ]

mikanSection = [
        [sg.Checkbox("Get newest page(s): ", key = "ifclassic", default = True, enable_events = True), sg.Push(), sg.Input("1", size = (20, 1), key = "classicnum")],
        [sg.Checkbox("Search each keyword in file: ", key = "ifsearch", default = True), sg.Push(), sg.Input(searchlist, size = (20, 1), key = "searchlist")],
        [sg.Checkbox("Get bangumi list for titles in file: ", key = "ifbangumi", default = True), sg.Push(), sg.Input(bangumilist, size = (20, 1), key = "bangumilist")],
        [sg.Checkbox("Generate bangumi list for search result", key = "ifSerToBan")],
        [sg.Checkbox("Torrent link", key = "iftorrent"), sg.Checkbox("Magnet link", key = "ifmagnet", default = True)],
        [sg.Text("", size = (60, 1))]
    ]

proxyFrame = sg.Frame("Proxy Section", proxySection, key = "proxyFrame")
mkanFrame = sg.Frame("Settings of getting Mikan", mikanSection)

layout = [[sg.Checkbox("Using proxy", default = True, key = "enableProxy", enable_events = True)],
        [proxyFrame],
        [mkanFrame],
        [sg.Button("Start")]
        ]

window = sg.Window("Mikan To My Plate", layout)

while True:
    event, values = window.read()  

    if values["enableProxy"] == False:
        window["proxyFrame"].update(visible = False)
    if values["enableProxy"] == True:
        window["proxyFrame"].update(visible = True)

    if values["downloadFromURL"] == False:
        window["proxylink"].update(visible = False)
        window["workingproxies"].update(disabled = False) 
        window["threads"].update(value = "1")
        window["threads"].update(disabled = True)
    if values["downloadFromURL"] == True:
        window["proxylink"].update(visible = True)
        window["workingproxies"].update(disabled = True) 
        window["threads"].update(value = "10")
        window["threads"].update(disabled = False)
    
    if values["ifclassic"] == False:
        window["classicnum"].update(value = "0")
        window["classicnum"].update(disabled = True)
    if values["ifclassic"] == True:
        window["classicnum"].update(value = "1")
        window["classicnum"].update(disabled = False)

    if event == sg.WIN_CLOSED:
        print("close")
        break

    if event == "Start":        
        try:
            classic_page_range = int(values["classicnum"])
        except:
            sg.popup("It's not a valid page number for \"Get newest page(s): \"")
            continue

        if classic_page_range < 0:
            sg.popup("It's not a valid page number for \"Get newest page(s): \"")
            continue

        try:
            threads = int(values["threads"])
        except:
            sg.popup("It's not a valid number for \"Number of threads for proxy check\"")
            continue

        if threads < 1:
            sg.popup("It's not a valid page number for \"Number of threads for proxy check\"")
            continue

        bangumilist = values["bangumilist"]
        searchlist = values["searchlist"]
        workingproxies = values["workingproxies"]
        proxylink = values["proxylink"]

        mikan = Mikan()
        mikan.start_migan(classic_page_range, values["ifsearch"], values["ifbangumi"], values["ifSerToBan"], values["enableProxy"], 
            values["downloadFromURL"], threads,
            values["iftorrent"], values["ifmagnet"], 
            searchlist, bangumilist,
            workingproxies, proxylink) 

        sg.popup("Mikan comes to the plate, enjoy!")   

window.close()

