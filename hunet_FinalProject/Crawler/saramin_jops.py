# %%
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time, math, os, random, urllib, urllib.request, getpass, re, datetime

# %%
username = getpass.getuser()    # getpass 모듈로 username 불러오기
# username = 'yzz07'
Services = Service('C:/Users/' + username + '/Desktop/chromedriver.exe')
driver = webdriver.Chrome(service=Services)

name = 'saramin_'  # 저장할 파일명
time_local = time.localtime()
time_name = ('%d.%d.%d_' % (time_local.tm_year,
             time_local.tm_mon, time_local.tm_mday))

save_location = 'C:\\Users\\' + username + '\\Desktop'
save_name = save_location + '\\' + name

if os.path.exists(save_name) == False:
    os.mkdir(save_name)
    os.chdir(save_name)
else:
    os.chdir(save_name)

today = datetime.datetime.today()

# %%

dic_category = {2: 'IT개발·데이터', 3: '회계·세무·재무', 4: '총무·법무·사무',
                5: '인사·노무·HRD', 6: '의료', 7: '운전·운송·배송',
                8: '영업·판매·무역', 9: '연구·R&D', 10: '서비스', 11: '생산',
                12: '상품기획·MD', 13: '미디어·문화·스포츠',
                14: '마케팅·홍보·조사', 15: '디자인', 16: '기획·전략',
                17: '금융·보험', 18: '구매·자재·물류', 19: '교육',
                20: '공공·복지', 21: '고객상담·TM', 22: '건설·건축'}

for key, value in dic_category.items():
    categorys = key
    cgname = value
    url = 'https://www.saramin.co.kr/zf_user/jobs/list/job-category?cat_mcls=%s&panel_type=&search_optional_item=n&search_done=y&panel_count=y' %categorys
    driver.get(url)
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    soups = soup.find('div', 'common_recruilt_list')
    content = soups.find('div', 'list_body').find_all('div')

    total_count = soup.find('span', 'total_count').get_text()
    total_count = re.sub('[^0-9]', '', total_count)
    print('Categories to collect : ' + cgname)
    print('Number of posts that can be collected : ' + total_count)
    int_total_count = int(total_count)

    data_main = []  # 대분류
    data_middle = []  # 중분류
    data_type = []  # 고용형태
    data_career = []  # 경력
    data_education = []  # 학력
    data_region = []  # 지역
    data_title = []  # 제목
    data_company = []  # 기업 이름
    data_deadline = []  # 마감일
    data_notice = []  # 공고일

    sum_count = 0
    page_count = 0
    page_counts = 0
    
    try:
        while True:
            time.sleep(1)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            content = soup.find('div', 'common_recruilt_list').find_all(
                'div', 'list_item')

            for content in content:

                data_main_ = cgname
                data_main.append(data_main_)

                data_middle_ = content.find('span', 'job_sector')
                data_middle_s = ''  # 관련 직무
                for i in data_middle_:
                    data_middle_s += i.text
                    data_middle_s += ', '
                data_middle.append(data_middle_s[:-2])

                try:   # 고용형태
                    data_type_ = content.find('p', 'employment_type').text
                except:
                    data_type_ = '-'
                data_type.append(data_type_)

                data_career_ = content.find('p', 'career').text
                if data_career_.find('↑'):
                    data_career_ = data_career_.replace('↑', ' 이상')
                data_career.append(data_career_)  # 경력

                data_education_ = content.find('p', 'education').text
                if data_education_.find('↑'):
                    data_education_ = data_education_.replace('↑', ' 이상')
                data_education.append(data_education_)  # 학력

                try:
                    data_region_ = content.find('p', 'work_place').text
                except:
                    data_region_ = '-'
                data_region.append(data_region_)  # 지역

                data_title_ = content.find('div', 'job_tit').span.text
                data_title.append(data_title_)  # 제목

                data_company_ = content.find('a', 'str_tit').text
                data_company.append(data_company_)  # 회사 이름

                try:
                    data_deadline_ = content.find('p', 'deadlines').text
                    data_deadline_ = data_deadline_.split('(')
                    data_deadline_ = datetime.datetime.strptime(
                        data_deadline_[0], '~ %m/%d')
                    data_deadline.append(
                        data_deadline_.strftime('2022-%m-%d'))  # 마감일
                except:
                    data_deadline.append('채용시')

                data_notice_ = content.find(
                    'p', 'deadlines').find('span', 'reg_date').text
                data_notice_1 = re.sub('[^0-9]', '', data_notice_)
                data_notice_ = today - \
                    datetime.timedelta(days=int(data_notice_1))
                data_notice.append(data_notice_.strftime('%Y-%m-%d'))  # 공고일

                sum_count += 1
                if int_total_count <= sum_count:
                    break

            if int_total_count <= sum_count:
                break

            page_count += 1

            if page_count == 11 and page_counts == 0:
                page_count = 2
                page_counts = 1

            elif page_count == 12:
                page_count = 2

            time.sleep(0.3)
            driver.find_element(
                By.XPATH, '//*[@id="default_list_wrap"]/div[3]/a[%s]' % page_count).click()

    except:
        print('An error occurred during collection.')

    print('Number of collected : ', sum_count)

    df = pd.DataFrame()
    df['main'] = pd.Series(data_main)
    df['middle'] = pd.Series(data_middle)
    df['type'] = pd.Series(data_type)
    df['career'] = pd.Series(data_career)
    df['education'] = pd.Series(data_education)
    df['region'] = pd.Series(data_region)
    df['title'] = pd.Series(data_title)
    df['company'] = pd.Series(data_company)
    df['deadline'] = pd.Series(data_deadline)
    df['notice'] = pd.Series(data_notice)

    ft_name = (cgname + '_' + time_name + name + '.txt')
    fc_name = (cgname + '_' + time_name + name + '.csv')
    fx_name = (cgname + '_' + time_name + name + '.xls')

    df.to_excel(fx_name, index=False, encoding="utf-8", engine='openpyxl')
    df.to_csv(fc_name, index=False, encoding="utf-8-sig")
    print('-' * 50)

print('작업이 완료되었습니다.')