import random

from moviepy.editor import CompositeVideoClip
from functions import *


def video_with_back_videos(script, script_number=1, voice_accent="en_us_006", voice_save_folder="__voice",
                           video_quality=720, background_video_path=None, back_videos_folder_path=None,
                           background_music_path=None, background_music_folder_path="__back_music",
                           gen_voice_volume=2.2, background_music_volume=0.3):
    gen_voice_path = generate_voice(script=script, script_number=script_number,
                                    voice=voice_accent, save_folder=voice_save_folder)
    if gen_voice_path != "Script have some problem":
        subtitle_details = get_subtitles_details(voice_path=gen_voice_path, video_num=script_number,
                                                 image_quality=video_quality, script=script)
        gen_voice = AudioFileClip(gen_voice_path)
        voice_duration = gen_voice.duration

        back_video = get_random_video_clip(video_duration=voice_duration, video_quality=video_quality,
                                           background_video_path=background_video_path,
                                           folder_path=back_videos_folder_path)
        audio_processed_video = process_video_with_audio(video_file=back_video, voice_file=gen_voice,
                                                         voice_volume=gen_voice_volume,
                                                         back_music_volume=background_music_volume,
                                                         background_music_path=background_music_path,
                                                         background_music_folder_path=background_music_folder_path)
        sub_title_clips = [audio_processed_video]
        for subs in subtitle_details:
            details = ImageClip(subs[-1], duration=subs[-2]).set_start(subs[-3])
            sub_title_clips.append(details)

        final_processed_video = CompositeVideoClip(sub_title_clips)
        final_processed_video.write_videofile("test.mp4")
    else:
        print(f"Sorry something wrong with the number {script_number} script")


def video_with_back_images(script, script_number=1, voice_accent="en_us_006", voice_save_folder="__voice",
                           video_quality=720, background_image_path=None, back_images_folder_path="__back_image",
                           background_music_path=None, background_music_folder_path="__back_music", fps=10,
                           gen_voice_volume=2.2, background_music_volume=0.3, random_images=False, image_gap=1):
    gen_voice_path = generate_voice(script=script, script_number=script_number, voice=voice_accent,
                                    save_folder=voice_save_folder)

    image_clips = []
    if gen_voice_path != "Script have some problem":
        subtitle_details = get_subtitles_details(voice_path=gen_voice_path, video_num=script_number,
                                                 image_quality=video_quality, script=script)
        gen_voice = AudioFileClip(gen_voice_path)
        voice_duration = gen_voice.duration

        image_paths = get_file_paths_from_folder(folder_path=back_images_folder_path)
        durations = get_all_the_image_durations(total_duration=voice_duration, num_of_image=len(image_paths),
                                                gap=image_gap)
        if random_images:
            random.shuffle(image_paths)

        timer = 0
        for time, img in enumerate(image_paths):
            this_image_duration = float(durations[time])
            if this_image_duration < 1:
                fade_time = this_image_duration / 12
            else:
                fade_time = this_image_duration / 8
            img_clip = image_adjust_for_video(image_path=img, image_quality=video_quality)

            if time == 0:  # First clip
                img_clip = img_clip.set_start(timer).set_duration(this_image_duration).set_fps(fps) \
                    .set_position("center", "center").fadeout(fade_time)
            elif time == len(image_paths) - 1:  # Last clip
                img_clip = img_clip.set_start(timer).set_duration(this_image_duration).set_fps(fps) \
                    .set_position("center", "center").fadein(fade_time)
            else:  # Clips in between
                img_clip = img_clip.set_start(timer).set_duration(this_image_duration).set_fps(fps) \
                    .set_position("center", "center").fadein(fade_time).fadeout(fade_time)

            timer += this_image_duration
            image_clips.append(img_clip)

        back_video = CompositeVideoClip(image_clips)

        audio_processed_video = process_video_with_audio(video_file=back_video, voice_file=gen_voice,
                                                         voice_volume=gen_voice_volume,
                                                         back_music_volume=background_music_volume,
                                                         background_music_path=background_music_path,
                                                         background_music_folder_path=background_music_folder_path)
        sub_title_clips = [audio_processed_video]
        for subs in subtitle_details:
            details = ImageClip(subs[-1], duration=subs[-2]).set_start(subs[-3])
            sub_title_clips.append(details)

        final_processed_video = CompositeVideoClip(sub_title_clips)
        final_processed_video.write_videofile("test.mp4")

    else:
        print(f"Sorry something wrong with the number {script_number} script")


def draw_rect(self, image, width, height, x_center, transparency=255, stroke=True, center_y=0):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if center_y == 0:
        center_y = (self.cover_h - height) // 2

    x_start = x_center - width // 2
    x_end = x_start + width
    square_coordinates = (x_start, center_y, x_end, center_y + height)

    transparent_white = (255, 255, 255, transparency)
    transparent_outline = (255, 174, 0, transparency)

    if stroke:
        draw.rounded_rectangle(square_coordinates, radius=50,
                               fill=transparent_white, outline=transparent_outline,
                               width=self.rect_stroke_thickness)
    else:
        draw.rounded_rectangle(square_coordinates, radius=50,
                               fill=transparent_white, width=self.rect_stroke_thickness)
    image = Image.alpha_composite(image, overlay)

    return image


def make_watermark_image(watermark, font_path='___temps/sub.ttf', image_quality=720,
                         fill_color="white", stroke_color="black", stroke_width=10):
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
        text_width, text_height = draw.textsize(watermark, font=font)
        if text_width >= max_font_width or text_height >= max_font_height:
            break
        elif minimum_font_size >= max_font_size:
            break
        minimum_font_size += 1

    x = (width - text_width) // 2
    y = 1080

    draw.text((x, y), watermark, font=font, fill=fill_color)

    # Resize the image based on the specified quality and ratio
    new_width = image_quality
    new_height = int(image_quality * (ratio[1] / ratio[0]))
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)

    resized_image.show()


if __name__ == "__main__":
    video_with_back_videos(script="hi hello, how are you?", script_number=2)

