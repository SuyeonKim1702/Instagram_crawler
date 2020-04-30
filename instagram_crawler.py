from selenium import webdriver
from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.keys import Keys
from multiprocessing import Pool,Manager
import pandas as pd
import openpyxl

#엑셀에 저장하기 위함
wb = openpyxl.Workbook()
sheet = wb.active


driver=webdriver.Chrome(
    executable_path="../webdriver/chromedriver.exe"
)
url="https://www.instagram.com/explore/tags/"
search = "" #본인이 원하는 해쉬태그 작성
url=url+search
driver.get(url) #enter 치는 것
sleep(5)

SCROLL_PAUSE_TIME = 3.5
reallink = []
likes_list=[]
follower=[]
used_url=[]
n=0

while True:
    pageString = driver.page_source
    bsObj = BeautifulSoup(pageString)
    # 각 사진들의 원주소를 가져옴
    # 스크롤을 내리며 사진들을 받아옴
    for link1 in bsObj.find_all(name="div", attrs={"class": "Nnq7C weEfm"}):
        title = link1.select('a')[0]
        real = title.attrs['href']
        if real not in (reallink):
          reallink.append(real)
        title = link1.select('a')[1]
        real = title.attrs['href']
        if real not in (reallink):
          reallink.append(real)
        title = link1.select('a')[2]
        real = title.attrs['href']
        if real not in (reallink):
          reallink.append(real)

    #1000개 이상의 사진을 받아오면 break
    if len(reallink)>1000:
        break
    last_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        else:
            last_height = new_height
            continue

reallinknum = len(reallink)
print("총" + str(reallinknum) + "개의 데이터를 받아왔습니다.")

try:
    for i in reallink:
        #각 게시글의 링크
        second = 'https://www.instagram.com' + i
        print(second)
        driver.get(second)
        html2 = driver.page_source
        soup = BeautifulSoup(html2)
        # print(soup)
        # txt에는 좋아요 수가 담긴 스트링이 담겨 있음...
        txt = soup.select('.sqdOP.yWX7d._8A5w5')
        #포스팅마다 구조가 조금씩 다름 ...
        if ((txt is None) or (txt[1].span is None) or (soup.select_one('.KL4Bh') is None)):

            continue

        else:
            # 사진 한장 가져옴
            imgUrl = soup.select_one('.KL4Bh').img['src']
           # with urlopen(imgUrl) as f:
            #    with open('name' + str(n) + '.jpg', 'ab') as h: # 사진 저장
            #        img = f.read()
             #       h.write(img)
            #n = n + 1
            print('이미지 경로:',imgUrl)

            #좋아요 수 가져오기
            insta2 = txt[1].span.get_text()
            insta2 = insta2.replace(',', '').strip()
            likes = int(insta2)
            likes_list.append(likes)

            # 팔로우 수 가져오기
            account_Url = soup.select('.sqdOP.yWX7d._8A5w5.ZIAjV')
            k = account_Url[0].attrs['href']
            third = 'https://www.instagram.com' + k
            driver.get(third)
            sleep(2)

            print(third)
            html3 = driver.page_source
            soup = BeautifulSoup(html3)
            j = soup.select('.g47SY')
            follower_num = j[1].attrs['title']
            follower_num = follower_num.replace(',', '').strip()
            follower_num = int(follower_num)
            follower.append(follower_num)
            data1 = pd.DataFrame(likes_list)
            data1.to_csv('likes_test.txt', header=False, encoding='utf-8')
            data2 = pd.DataFrame(follower)
            data2.to_csv('follower_test.txt', header=False, encoding='utf-8')

            print('팔로워 수:', follower[-1])
            print('좋아요 수:', likes_list[-1])
            if len(likes_list) == len(follower):
               sheet.append([follower[-1],likes_list[-1]])
            else:
                raise Exception


except Exception as ex:
    print("에러발생:", ex)

    if len(likes_list) != len(follower):
        print("팔로워 수/좋아요 수 불일치")



driver.close()
wb.save('name') #엑셀 파일 저장
