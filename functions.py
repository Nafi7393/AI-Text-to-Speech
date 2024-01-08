import os
import random
import re
import shutil
import textwrap
import warnings
import tiktokvoice
import whisper_timestamped
import numpy as np
from natsort import natsorted
from decimal import Decimal, getcontext
from moviepy.editor import concatenate_audioclips, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, VideoFileClip, CompositeAudioClip, ImageClip

warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ['PATH'] += os.pathsep + '___temps\\FFmpeg\\bin'


def image_adjust_for_video(image_path, image_quality=720):
    original_image = Image.open(image_path)
    desired_ratio = (9, 16)
    image_aspect_ratio = original_image.width / original_image.height

    final_width = image_quality
    final_height = int((desired_ratio[1] / desired_ratio[0]) * image_quality)

    new_width = int(final_height * image_aspect_ratio)
    resized_image = original_image.resize((new_width, final_height))

    new_canvas = Image.new("RGBA", (final_width, final_height), "white")
    position = ((final_width - resized_image.width) // 2, (final_height - resized_image.height) // 2)
    new_canvas.paste(resized_image, position)

    image_array = np.array(new_canvas)

    return ImageClip(image_array)


def get_file_paths_from_folder(folder_path, return_all_files=True):
    all_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]

    folders = [folder for folder in all_files if os.path.isdir(folder)]
    files = [file for file in all_files if os.path.isfile(file)]

    if not files:
        random_folder = random.choice(folders)
        files = [os.path.join(random_folder, file) for file in os.listdir(random_folder) if
                 os.path.isfile(os.path.join(random_folder, file))]

    if return_all_files:
        return natsorted(files)
    else:
        return random.choice(files)


def make_reddit_first_image(title, story_sync_with_folder_num=1, font_path='___temps/subtitle.ttf',
                            image_quality=720, base_img_path="___temps/reddit.png"):
    text_left_margin = 110
    min_text_height = 585
    ratio = (9, 16)

    base_img = Image.open(base_img_path).convert("RGBA")
    draw = ImageDraw.Draw(base_img)

    chosen_font_size = 46
    para = textwrap.wrap(title, width=41)
    font = ImageFont.truetype(font_path, chosen_font_size)

    pad = 18
    current_height = min_text_height
    for line in para:
        text_width, text_height = draw.textsize(line, font=font)

        y_position = current_height

        draw.text((text_left_margin, y_position), line, font=font, fill="black")
        current_height += text_height + pad

    new_width = image_quality
    new_height = int(image_quality * (ratio[1] / ratio[0]))

    rgba = base_img.convert("RGBA").resize((new_width, new_height), Image.ANTIALIAS)
    rgba.save(f"__gen_images/{story_sync_with_folder_num}.png")
    return f"__gen_images/{story_sync_with_folder_num}.png"


def make_sub_images(word, word_num=1, folder_num=1, image_quality=720, font_path='___temps/subtitle.ttf',
                    fill_color="white", stroke_color="black", stroke_width=10):

    word = word.replace(",", "")
    words = word.split('-')

    ratio = (9, 16)
    width, height = (720, 1280)

    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    minimum_font_size = 10
    max_font_size = 150
    width_bounding_box = 150
    max_font_width, max_font_height = width - width_bounding_box, height

    for i, word_part in enumerate(words):
        while True:
            font = ImageFont.truetype(font_path, minimum_font_size)
            text_width, text_height = draw.textsize(word_part, font=font)
            if text_width >= max_font_width or text_height >= max_font_height:
                break
            elif minimum_font_size >= max_font_size:
                break
            minimum_font_size += 1

        x = (width - text_width) // 2
        y = (height - text_height * len(words)) // 2 + i * text_height
        draw.text((x, y - 150), word_part, font=font, fill=fill_color,
                  stroke_width=stroke_width, stroke_fill=stroke_color)
        minimum_font_size = 10

    # Resize the image based on the specified quality and ratio
    new_width = image_quality
    new_height = int(image_quality * (ratio[1] / ratio[0]))
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)

    image_array = np.array(resized_image)
    return image_array

    # if not os.path.exists(f"__gen_images/{folder_num}"):
        # os.makedirs(f"__gen_images/{folder_num}")

    # resized_image.save(f"__gen_images/{folder_num}/{word_num}.png")
    # return f"__gen_images/{folder_num}/{word_num}.png"


def get_available_voices():
    return tiktokvoice.VOICES_DICT


def get_line_chunks(paragraph, line_length=300):
    if paragraph[-1] not in [".", "!", "?"]:
        paragraph += "."

    result = re.split(r'([.?!]+)', paragraph)
    result = [result[i] + result[i + 1] for i in range(0, len(result) - 1, 2)]

    wrapped_lines = []
    ellipsis_at_end = False

    for sentence in result:
        if sentence.endswith("..."):
            sentence = sentence.rstrip(".")  # Remove trailing dot to keep the ellipsis
            ellipsis_at_end = True
        else:
            ellipsis_at_end = False

        words = sentence.split()
        current_line = ""

        for word in words:
            if len(current_line + word) <= line_length:
                current_line += word + " "
            else:
                wrapped_lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            wrapped_lines.append(current_line.strip() + ("..." if ellipsis_at_end else ""))

    return wrapped_lines


def get_scripts(file_path='_SCRIPTs.txt'):
    with open(file_path, 'r') as file:
        scripts = file.readlines()

    all_scripts = [script.strip() for script in scripts]
    return all_scripts


def select_random_clips(video_duration, video_quality=720, folder_path="__back_video"):
    selected_clips = []
    used_path = []
    total_duration = 0
    left_duration = video_duration
    selected_size = []

    while total_duration < video_duration:
        background_video_path = random.choice(get_file_paths_from_folder(folder_path))

        if background_video_path not in used_path:
            video_clip = VideoFileClip(background_video_path).resize((1080, 1920)).resize(width=video_quality)
            clip_duration = video_clip.duration

            if total_duration + clip_duration <= video_duration:
                selected_clips.append(video_clip)
                total_duration += clip_duration
                left_duration -= clip_duration
            else:
                sub_video_clip = video_clip.subclip(0, left_duration)
                selected_clips.append(sub_video_clip)
                total_duration = video_duration
        else:
            continue

    return selected_clips


def get_random_video_clip(video_duration, video_quality=720, background_video_path=None, folder_path=None):
    if folder_path is None:
        folder_path = "__back_video"

    if background_video_path is None:
        provided = False
        background_video_path = random.choice(get_file_paths_from_folder(folder_path))

    else:
        provided = True

    video_clip = VideoFileClip(background_video_path).resize((1080, 1920)).resize(width=video_quality)
    clip_duration = video_clip.duration

    if clip_duration < video_duration and provided:
        raise ValueError(f"{background_video_path} Duration is lower than desired subclip duration")

    if clip_duration < video_duration:
        selected_clips = select_random_clips(video_duration, folder_path=folder_path, video_quality=video_quality)
        final_clip = concatenate_videoclips(selected_clips)
        return final_clip
    else:
        start_time = random.uniform(0, clip_duration - (video_duration + 1))
        sub_video_clip = video_clip.subclip(start_time, start_time + video_duration)
        return sub_video_clip


def generate_voice(script, script_number=1, voice="en_us_006", save_folder="__voice"):
    results = get_line_chunks(script)
    audios = []

    if not os.path.exists(f"{save_folder}/Script_{script_number}"):
        os.makedirs(f"{save_folder}/Script_{script_number}")

    for line_num, line in enumerate(results, start=1):
        gen = tiktokvoice.tts(line, voice, f"{save_folder}/Script_{script_number}/{line_num}_output.mp3")
        if gen == "All Good":
            audios.append(AudioFileClip(f"{save_folder}/Script_{script_number}/{line_num}_output.mp3"))
        else:
            return f"Script have some problem"

    this_audio = concatenate_audioclips(audios)
    this_audio.write_audiofile(f"{save_folder}/Script_{script_number}_VOICE.wav", fps=44100, codec='pcm_s16le')

    for audio in audios:
        audio.close()
    shutil.rmtree(f"{save_folder}/Script_{script_number}")

    return f"{save_folder}/Script_{script_number}_VOICE.wav"


def get_line_and_voice(script='_SCRIPTs.txt', voice_folder="__voice"):
    lines = get_scripts(file_path=script)
    generated_voices = []
    if len(lines) != len(os.listdir(voice_folder)):
        for i, line in enumerate(lines, start=1):
            generated_voices.append(generate_voice(line, i))
    else:
        generated_voices = [os.path.join(voice_folder, file) for file in os.listdir(voice_folder)]

    return zip(lines, natsorted(generated_voices))


def get_subtitles_details(voice_path, video_num, image_quality=720, sub_font_path='___temps/subtitle.ttf', script=None):
    model = whisper_timestamped.load_model("base")
    transcribe_result = whisper_timestamped.transcribe(model, voice_path)

    all_subtitle_details = []
    file_num = 0

    for segment in transcribe_result["segments"]:
        for _word in segment["words"]:
            text = _word["text"].upper()

            start = _word["start"]
            end = _word["end"]
            duration = end - start

            sub_img_clip_path = make_sub_images(text, file_num, video_num,
                                                image_quality=image_quality, font_path=sub_font_path)

            details = [file_num, text, start, duration, sub_img_clip_path]
            all_subtitle_details.append(details)

            file_num += 1

    return all_subtitle_details


def process_video_with_audio(video_file, voice_file,
                             background_music_path=None, background_music_folder_path="__back_music",
                             voice_volume=2.2, back_music_volume=0.3):
    if background_music_path is None:
        background_music_path = random.choice(get_file_paths_from_folder(folder_path=background_music_folder_path))
    back_music = AudioFileClip(background_music_path)
    back_music_full_duration = back_music.duration

    duration = voice_file.duration

    start = random.uniform(0, back_music_full_duration-duration)
    end = start + duration
    back_music = back_music.subclip(t_start=start, t_end=end)

    final_audio = CompositeAudioClip([voice_file.volumex(voice_volume), back_music.volumex(back_music_volume)])
    processed_video_file = video_file.set_audio(final_audio)

    return processed_video_file


def get_all_the_image_durations(total_duration, num_of_image, gap=1, generation_num=0):
    if isinstance(total_duration, float):
        getcontext().prec = 16
        total = Decimal(str(f'{total_duration}'))
        int_part = int(total)
        float_part = total - int_part
        is_it_float = True
    else:
        total = total_duration
        int_part = total_duration
        float_part = Decimal(str("0.00"))
        is_it_float = False

    divisions = []
    max_value = int(total/(num_of_image+1))

    low_gap = max_value-gap
    max_gap = max_value+gap

    if low_gap < 0:
        max_gap = 0
        low_gap = 1

    for i in range(num_of_image):
        divisions.append(Decimal(str(random.uniform(low_gap, max_gap))))

    remain = int_part - sum(divisions) + float_part
    if remain < 0:
        remain = (sum(divisions) - int_part) + float_part

    sub_parts = remain/(remain+200)
    while remain > 0:
        random.shuffle(divisions)
        divisions[0] += sub_parts
        remain -= sub_parts

    extra = sum(divisions) - total
    sub_extra_parts = extra / 10
    if extra > 0:
        while extra > 0:
            random.shuffle(divisions)
            divisions[0] -= sub_extra_parts
            extra -= sub_extra_parts
    if extra < 0:
        while extra < 0:
            random.shuffle(divisions)
            divisions[0] += sub_extra_parts
            extra -= sub_extra_parts

    if all(num > 0 for num in divisions):
        return divisions
    elif generation_num >= 5:
        return "Sorry can't do this"
    else:
        return get_all_the_image_durations(total_duration=total_duration, num_of_image=num_of_image,
                                           generation_num=generation_num+1)


def draw_rect(image, width, height, x_center, transparency=255, stroke=True, center_y=0,
              rect_color=(255, 255, 255), rect_outline_color=(255, 174, 0)):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if center_y == 0:
        center_y = (image.height - height) // 2

    x_start = x_center - width // 2
    x_end = x_start + width
    square_coordinates = (x_start, center_y, x_end, center_y + height)

    transparent_rect_color = (rect_color[0], rect_color[1], rect_color[2], transparency)
    transparent_outline_color = (rect_outline_color[0], rect_outline_color[1], rect_outline_color[2], transparency)

    if stroke:
        draw.rounded_rectangle(square_coordinates, radius=50,
                               fill=transparent_rect_color, outline=transparent_outline_color)
    else:
        draw.rounded_rectangle(square_coordinates, radius=50, fill=transparent_rect_color)
    image = Image.alpha_composite(image, overlay)

    return image


def make_watermark_image(watermark_txt, font_path='___temps/subtitle.ttf', image_quality=720, text_fill_color=(255, 255, 255),
                         stroke_color=None, stroke_width=0, back_rect=True, rect_transparency=100, rect_stroke=False,
                         back_rect_color=(255, 255, 255), back_rect_outline_color=(255, 174, 0)):
    ratio = (9, 16)
    width, height = (720, 1280)

    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    minimum_font_size = 1
    max_font_size = 30
    width_bounding_box = 150
    max_font_width, max_font_height = width - width_bounding_box, height

    while True:
        font = ImageFont.truetype(font_path, minimum_font_size)
        text_width, text_height = draw.textsize(watermark_txt, font=font)
        if text_width >= max_font_width or text_height >= max_font_height:
            break
        elif minimum_font_size >= max_font_size:
            break
        minimum_font_size += 1

    x = (width - text_width) // 2
    y = 1080

    draw.text((x, y), watermark_txt, font=font, fill=text_fill_color,
              stroke_color=stroke_color, stroke_width=stroke_width)

    if back_rect:
        rect_width = text_width + 50
        rect_height = text_height + (text_height*0.2)
        rect_x_center = width // 2
        rect_center_y = y + text_height // 2 - (text_height/2)

        image = draw_rect(image=image, width=rect_width, height=rect_height, x_center=rect_x_center,
                          transparency=rect_transparency, stroke=rect_stroke, center_y=rect_center_y,
                          rect_color=back_rect_color, rect_outline_color=back_rect_outline_color)

    new_width = image_quality
    new_height = int(image_quality * (ratio[1] / ratio[0]))
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)

    image_array = np.array(resized_image)
    return ImageClip(image_array)








