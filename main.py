import threading
from workspace import *

warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ['PATH'] += os.pathsep + '___temps\\FFmpeg\\bin'


def fire_baby():
    limit = 0
    all_task = []

    paired_files = get_line_and_voice()
    num_video = 1
    for _line, _voice_path in paired_files:
        limit += 1
        thread = threading.Thread(target=make_final_video, args=(_line, _voice_path, num_video))
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
    pass
