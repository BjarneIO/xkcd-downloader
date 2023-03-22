import os
import re
import httpx

BASE_URL = 'https://xkcd.com'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}

session = httpx.Client(headers=HEADERS, follow_redirects=True)

os.makedirs('comics',exist_ok = True)

# Get the latest comic number
res = session.get(BASE_URL, follow_redirects=True)
latest_comic_number = re.search(r'<a href="https://xkcd.com/(.*?)">', res.text).group(1)
latest_comic_number = int(latest_comic_number) + 1

# Get the amount of comics in the './comics/' folder
comics_in_folder = len(os.listdir('comics')) 

# Download the comics
for comic_num in range(comics_in_folder + 2, latest_comic_number):
    
    res = session.get(f'{BASE_URL}/{comic_num}')
    if res.status_code != 200:
        continue
    
    # This comic is an interactive one, so we skip it
    if 'panel' in res.text:
        continue

    img_src = re.search(r'<img src="(.*?)" title="', res.text).group(1)
    img_src = img_src.replace('//', 'https://')

    comic_title = re.search(r'<div id="ctitle">(.*?)</div>', res.text).group(1)
    comic_title = re.sub(r'[\\/:*?"<>|]', '', comic_title) # Remove illegal file name characters

    # Download and save the image
    comic_file_name = f'{comic_num} {comic_title}'
    with open(os.path.join('comics', f'{comic_file_name}.jpg'), 'wb') as f:
        f.write(session.get(img_src).content)

    print(f'Downloaded {comic_file_name}')
    
session.close()
