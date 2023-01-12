import requests
import parsel
import re
import uuid
import os

FILE_NAME_REGEX = re.compile(r"filename=\"(?P<filename>.+)\"")

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'

URL = 'https://film-grab.com/page/18/'

if not os.path.exists('images'):
    os.makedirs('images')

def main():
    global URL
    with requests.session() as s:
        s.headers.update({'User-Agent': USER_AGENT})
        while URL is not None:
            print(f"Current URL: {URL}")
            html = s.get(URL).text
            page_data = parse_page(html)
            if page_data['movie_urls'] is not None:
                for movie_url in page_data['movie_urls']:
                    html = s.get(movie_url).text
                    download_data = download_movie_images(html, s)
                    if not download_data['success']:
                        with open('failed.txt', 'a') as log:
                            log.write(download_data['url'])
                        print(f'Failed to download: {download_data["file_name"]}')
                    else:
                        print(f'Successfully downloaded: {download_data["file_name"]}')
            URL = page_data['next_page']
        


def parse_page(html: str):
    page_data = {
        'movie_urls': None,
        'next_page': None,
    }
    selector = parsel.Selector(text=html)
    movie_urls = selector.xpath("//a[@class='popup-image']/@href").getall()
    if len(movie_urls) != 0:
        page_data['movie_urls'] = movie_urls
    
    next_page = selector.xpath("//a[@class='next page-numbers']/@href").get()
    if next_page is not None:
        page_data['next_page'] = next_page

    return page_data


def download_movie_images(html: str, s: requests.Session):
    download_info = {
        'success': False,
        'file_name': f'{str(uuid.uuid4())}.zip',
        'url': None
    }
    selector = parsel.Selector(text=html)
    movie_url = selector.xpath("//div[@class='bwg_download_gallery']/a/@href").get()
    if movie_url is None:
        return download_info
    download_info['url'] = movie_url
    
    response = s.get(movie_url)
    if response.status_code != 200:
        return download_info
    
    else:
        match_result = FILE_NAME_REGEX.search(response.headers['content-disposition'])
        if match_result is not None:
            download_info['file_name'] = match_result.group('filename')
        with open(os.path.join('images', download_info['file_name']), 'wb') as zip_file:
            zip_file.write(response.content)
            download_info['success'] = True
            return download_info









if __name__ == '__main__':
    main()