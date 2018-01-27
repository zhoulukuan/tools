import urllib.request
import re

def getHtml(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    html = html.decode('utf-8')
    return html

def download_file(download_url, file_name):
    response = urllib.request.urlopen(download_url)
    file = open(file_name, 'wb')
    file.write(response.read())
    file.close()
    print("Completed")

save_path = 'E:/paper/cvpr2017/'
url = 'http://openaccess.thecvf.com/CVPR2017.py'
html = getHtml(url)
parttern = re.compile(r'\bcontent_cvpr_2017.*paper\.pdf\b')
url_list = parttern.findall(html)

for url in url_list:
    name = url.split('/')[-1]
    file_name = save_path + name
    download_file('http://openaccess.thecvf.com/'+url, file_name)



