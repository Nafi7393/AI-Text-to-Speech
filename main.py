import threading
import csv
from workspace import *

warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ['PATH'] += os.pathsep + '___temps\\FFmpeg\\bin'


def get_all_scripts(csv_file_path='scripts.csv'):
    data_list = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')  # Change the delimiter to a comma
        for row in reader:
            if len(row) >= 2:
                title, script = row[0], row[1]
                data_list.append((title.strip(), script.strip()))
            else:
                # Handle the case where a row doesn't have enough values
                print(f"Skipping invalid row: {row}")

    return data_list


def fire_baby(script_path, script_number=1, voice_accent="en_us_006", voice_save_folder="__voice",
              video_quality=720, background_video_path=None, back_videos_folder_path=None,
              background_music_path=None, background_music_folder_path="__back_music",
              gen_voice_volume=2.2, background_music_volume=0.3, sub_font_path='___temps/subtitle.ttf',
              watermark=True, watermark_text="Money Magnet Mindset", image_fps=40,
              watermark_font_path='___temps/watermark.ttf', watermark_text_color=(255, 255, 255),
              watermark_stroke_color=None, watermark_stroke_width=0, watermark_back_react=True,
              watermark_rect_transparency=120, watermark_rect_stroke=False, watermark_fps=1,
              watermark_back_rect_color=(255, 255, 255), watermark_back_rect_outline_color=(255, 174, 0),
              output_location="test"):
    limit = 0
    all_task = []

    details_list = get_all_scripts(csv_file_path=script_path)
    num_video = 1
    for title, script in details_list:
        limit += 1
        thread = threading.Thread(target=video_with_back_videos, kwargs={'script': script,
                                                                         'voice_accent': voice_accent,
                                                                         'video_quality': video_quality,
                                                                         'watermark_text': watermark_text,
                                                                         'script_number': num_video,
                                                                         'back_videos_folder_path': back_videos_folder_path,
                                                                         'background_music_folder_path': background_music_folder_path,
                                                                         'background_music_volume': background_music_volume,
                                                                         'output_location': f"OUTPUT/{title}"})
        thread.start()
        all_task.append(thread)
        num_video += 1

        if limit == 6:
            for fire in all_task:
                fire.join()
            all_task = []
            limit = 0

    for fire in all_task:
        fire.join()


if __name__ == "__main__":
    fire_baby()
