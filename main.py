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


def fire_baby():
    limit = 0
    all_task = []

    details_list = get_all_scripts(csv_file_path="scripts.csv")
    num_video = 1
    for title, script in details_list:
        limit += 1
        thread = threading.Thread(target=video_with_back_videos, kwargs={'script': script,
                                                                         'script_number': num_video,
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
