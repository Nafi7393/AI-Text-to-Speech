from bs4 import BeautifulSoup
from pytube import YouTube
import threading


def get_links_for_short(file='short_video_link.html'):
    final_links = []

    with open(file, 'r', encoding='utf-8') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'html.parser')
    a_tags = soup.find_all('a', class_='yt-simple-endpoint')

    for a_tag in a_tags:
        href_value = "https://www.youtube.com" + a_tag.get('href')
        if href_value not in final_links:
            final_links.append(href_value)

    with open('short_vid_links.txt', 'w', encoding='utf-8') as output_file:
        for link in final_links:
            output_file.write(link + '\n')

    return final_links


def get_links_for_long(file='long_video_link.html'):
    final_links = []

    with open(file, 'r', encoding='utf-8') as file:
        html = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    # Find all div elements with the specified attributes
    div_elements = soup.find_all('div', {'id': 'contents'})

    # Iterate through the div elements and extract the href attribute
    for div_element in div_elements:
        a_elements = list(set(div_element.find_all('a', {'id': 'thumbnail'})))
        for a_element in a_elements:
            href_value = "https://www.youtube.com" + a_element.get('href')
            if href_value not in final_links:
                final_links.append(href_value)

    with open('long_vid_links.txt', 'w', encoding='utf-8') as output_file:
        for link in final_links:
            output_file.write(link + '\n')

    return final_links


def download_youtube_video(link, filename_prefix="VID___", path="videos"):
    youtube_object = YouTube(link)
    youtube_object = youtube_object.streams.get_highest_resolution()
    try:
        youtube_object.download(output_path=path, filename_prefix=filename_prefix)
    except Exception:
        print("An error has occurred")


def large_amount_download(download_links, num_tasks=20):
    threads = []

    for i, yt_link in enumerate(download_links, start=1):
        thread = threading.Thread(target=download_youtube_video, args=(yt_link, f"{i}_", "videos"))
        threads.append(thread)
        thread.start()

        if len(threads) >= num_tasks:
            for thread in threads:
                thread.join()
            threads = []
            print("DONE")

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    pass
