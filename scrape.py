import os
import httpx
from time import perf_counter

BASE_URL = 'https://xkcd.com'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}
COMIC_FOLDER = 'comics'


def get_latest_comic_number(session: httpx.Client) -> int:
    ''' Get the latest comic number '''
    res = session.get(f'{BASE_URL}/info.0.json').json()
    return int(res['num'])


def get_latest_local_comic() -> int:
    ''' Get the most recent comic number in the folder '''
    comics_in_folder = [int(file.split()[0]) for file in os.listdir(
        COMIC_FOLDER) if file.endswith('.png')]
    most_recent_comic_number = max(comics_in_folder) if comics_in_folder else 0

    return most_recent_comic_number


def get_comic_data(session: httpx.Client, comic_num: int) -> dict:
    ''' Get the comic data '''
    res = session.get(f'{BASE_URL}/{comic_num}/info.0.json')

    if res.status_code != 200:
        print(f'Skipped #{comic_num} (Status code {res.status_code})')
        return None

    return res.json()


def main():

    session = httpx.Client(headers=HEADERS, follow_redirects=True)
    os.makedirs(COMIC_FOLDER, exist_ok=True)

    latest_comic_number = get_latest_comic_number(session)
    most_recent_comic_number = get_latest_local_comic()

    print(f'Latest comic: #{latest_comic_number}')
    print(f'Comics in folder: #{most_recent_comic_number}')

    if most_recent_comic_number == latest_comic_number:
        print('All comics are up to date')
        session.close()
        return

    start_time = perf_counter()

    for comic_num in range(most_recent_comic_number + 1, latest_comic_number + 1):
        print(f'Downloading #{comic_num}')

        comic_data = get_comic_data(session, comic_num)

        if not comic_data or 'extra_parts' in comic_data:
            print(f'Skipped #{comic_num}')
            continue

        img_src = comic_data['img']
        comic_title = comic_data['safe_title']
        comic_file_name = f'{comic_num} {comic_title}.png'

        with open(os.path.join(COMIC_FOLDER, f'{comic_file_name}.jpg'), 'wb') as f:
            f.write(session.get(img_src).content)

        print(f'Downloaded #{comic_num} ({comic_title})')

    session.close()

    end_time = perf_counter()
    print(
        f'Downloaded {latest_comic_number - most_recent_comic_number} comics in {end_time - start_time:.2f} seconds')


if __name__ == '__main__':
    main()
