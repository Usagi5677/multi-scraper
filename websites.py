from bs4 import BeautifulSoup
import re
import time
import os

def get_urls(driver, link, **kwargs):
    injected = kwargs.get('injected', False)
    pause = kwargs.get('pause', 0)
    headless = kwargs.get('headless', True)

    if(pause > 0):
        time.sleep(pause)
    
    if(injected): #for example, instagram inject their content during initial page load. so, we need to wait for it to load the content
        time.sleep(1)
    
    driver.get(link)
    
    html = driver.execute_script("return document.body.innerHTML;")     #getting the inner html of body
    soup = BeautifulSoup(html, "html.parser") 
    img_tags = soup.find_all("img")
    urls = [img['src'] for img in img_tags] # get all img tags
    
    if not re.search(r"^https://", urls[0]):    # some url doesn't have https in the img tag so we'll need to check it and add
        urls = ["https:" + url for url in urls]
    
    if re.search(r"\breddit\.com\b", link): # reddit
        tags = soup.find_all('div', {'data-click-id': 'media'})
        urls = []
        
        for tag in tags:
            a_tag = tag.find('a')
            if a_tag is None or re.search(r"\balb\.reddit\.com\b", a_tag["href"]):
                continue
            
            url = "https://www.reddit.com" + a_tag["href"]
            urls.append(url)
        for i, url in enumerate(urls):
            if(pause > 0):
                time.sleep(pause)
            driver.get(url)
            if(injected):
                time.sleep(1)
                
            html = driver.execute_script("return document.body.innerHTML;")     #getting the inner html of body
            soup = BeautifulSoup(html, "html.parser") 

            tag = soup.find('div', {'data-post-click-location': 'post-media-content'})
            a_tag = tag.find('a')
            if(a_tag is None):
                continue
            urls[i] = a_tag["href"]
    #note: instagram blocks ip address if it thinks you're a bot. so, have to wait a while to reset. also, changing ip address works.
    elif re.search(r"\binstagram\.com\b", link): # instagram
        img_tags = soup.find_all("div", {"class": "_aabd"})
        urls = []
        for img_tag in img_tags:
            a_tag = img_tag.find('a')
            url = "https://www.instagram.com" + a_tag["href"]
            urls.append(url)
        for i, url in enumerate(urls):
            if(pause > 0):
                time.sleep(pause)

            driver.get(url)

            if(injected):
                time.sleep(1)
                
            html = driver.execute_script("return document.body.innerHTML;")     #getting the inner html of body
            soup = BeautifulSoup(html, "html.parser") 
            img_tag = soup.find("div", {"class": "_aagv"})
            img_tag = img_tag.find('img')
            urls[i] = img_tag['src']
    
    #nsfw
    elif re.search(r"boards\.4chan(?:nel)?\.org", link): # 4channel
        img_tags = soup.find_all("a", {"class": "fileThumb"})
        urls = [img['href'] for img in img_tags]
        if(headless):
            urls = ["https:" + url for url in urls]
        for i in range(len(urls)):
            parts = urls[i].split('.')
            if parts[-2].endswith('s'):
                parts[-2] = parts[-2][:-1]
            urls[i] = '.'.join(parts)

    #archives (nsfw)
    elif re.search(r"\bwarosu\.org\b", link): # warosu
        img_tags = soup.find_all("img", {"class": "thumb"})
        urls = []
        for img_tag in img_tags:
            parent_a_tag = img_tag.find_parent("a")
            url = "https:" + parent_a_tag["href"]
            parts = url.split('.')
            if parts[-2].endswith('s'):
                parts[-2] = parts[-2][:-1]
            url = '.'.join(parts)
            urls.append(url)
    elif re.search(r"\bdesuarchive\.org\b", link): # desu
        img_tags = soup.find_all("div", {"class": "thread_image_box"})
        urls = []
        for img_tag in img_tags:
            a_tag = img_tag.find("a")
            url = a_tag["href"]
            urls.append(url)
    
    return urls
  