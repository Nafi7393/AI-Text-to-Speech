from moviepy.editor import CompositeVideoClip
from functions import *


def video_with_back_videos(script, script_number=1, voice_accent="en_us_006", voice_save_folder="__voice",
                           video_quality=720, background_video_path=None, back_videos_folder_path=None,
                           background_music_path=None, background_music_folder_path="__back_music",
                           gen_voice_volume=2.2, background_music_volume=0.3, sub_font_path='___temps/subtitle.ttf',
                           watermark=True, watermark_text="Money Magnet Mindset", image_fps=40,
                           watermark_font_path='___temps/watermark.ttf', watermark_text_color=(255, 255, 255),
                           watermark_stroke_color=None, watermark_stroke_width=0, watermark_back_react=True,
                           watermark_rect_transparency=120, watermark_rect_stroke=False, watermark_fps=1,
                           watermark_back_rect_color=(255, 255, 255), watermark_back_rect_outline_color=(255, 174, 0),
                           output_location="test"):
    gen_voice_path = generate_voice(script=script, script_number=script_number,
                                    voice=voice_accent, save_folder=voice_save_folder)
    if gen_voice_path != "Script have some problem":
        subtitle_details = get_subtitles_details(voice_path=gen_voice_path, video_num=script_number, script=script,
                                                 image_quality=video_quality, sub_font_path=sub_font_path)
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

        if watermark:
            watermark_image = make_watermark_image(watermark_txt=watermark_text, font_path=watermark_font_path,
                                                   image_quality=video_quality, text_fill_color=watermark_text_color,
                                                   stroke_color=watermark_stroke_color,
                                                   stroke_width=watermark_stroke_width,
                                                   back_rect=watermark_back_react, rect_stroke=watermark_rect_stroke,
                                                   rect_transparency=watermark_rect_transparency,
                                                   back_rect_color=watermark_back_rect_color,
                                                   back_rect_outline_color=watermark_back_rect_outline_color)
            watermark_image = watermark_image.set_start(0).set_duration(voice_duration).set_fps(watermark_fps)\
                .set_position("center", "center")
            sub_title_clips.append(watermark_image)

        for subs in subtitle_details:
            details = ImageClip(subs[-1], duration=subs[-2]).set_start(subs[-3])
            sub_title_clips.append(details)

        final_processed_video = CompositeVideoClip(sub_title_clips)
        final_processed_video.write_videofile(f"{output_location}.mp4")
    else:
        print(f"Sorry something wrong with the number {script_number} script")


def video_with_back_images(script, script_number=1, voice_accent="en_us_006", voice_save_folder="__voice",
                           video_quality=720, background_image_path=None, back_images_folder_path="__back_image",
                           background_music_path=None, background_music_folder_path="__back_music",
                           gen_voice_volume=2.2, background_music_volume=0.3, sub_font_path='___temps/subtitle.ttf',
                           random_images=False, image_gap=1, image_fps=40,
                           watermark=True, watermark_text="Money Magnet Mindset",
                           watermark_font_path='___temps/watermark.ttf', watermark_text_color=(255, 255, 255),
                           watermark_stroke_color=None, watermark_stroke_width=0, watermark_back_react=True,
                           watermark_rect_transparency=120, watermark_rect_stroke=False,  watermark_fps=5,
                           watermark_back_rect_color=(255, 255, 255), watermark_back_rect_outline_color=(255, 174, 0),
                           output_location="test"):
    gen_voice_path = generate_voice(script=script, script_number=script_number, voice=voice_accent,
                                    save_folder=voice_save_folder)

    image_clips = []
    if gen_voice_path != "Script have some problem":
        subtitle_details = get_subtitles_details(voice_path=gen_voice_path, video_num=script_number, script=script,
                                                 image_quality=video_quality, sub_font_path=sub_font_path)
        gen_voice = AudioFileClip(gen_voice_path)
        voice_duration = gen_voice.duration

        if background_image_path is None:
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
                    img_clip = img_clip.set_start(timer).set_duration(this_image_duration).set_fps(image_fps) \
                        .set_position("center", "center").fadeout(fade_time)
                elif time == len(image_paths) - 1:  # Last clip
                    img_clip = img_clip.set_start(timer).set_duration(this_image_duration).set_fps(image_fps) \
                        .set_position("center", "center").fadein(fade_time)
                else:  # Clips in between
                    img_clip = img_clip.set_start(timer).set_duration(this_image_duration).set_fps(image_fps) \
                        .set_position("center", "center").fadein(fade_time).fadeout(fade_time)

                timer += this_image_duration
                image_clips.append(img_clip)
        else:
            img_clip = image_adjust_for_video(image_path=background_image_path, image_quality=video_quality)
            img_clip = img_clip.set_start(0).set_duration(voice_duration).set_fps(image_fps)\
                .set_position("center", "center")
            image_clips.append(img_clip)

        if watermark:
            watermark_image = make_watermark_image(watermark_txt=watermark_text, font_path=watermark_font_path,
                                                   image_quality=video_quality, text_fill_color=watermark_text_color,
                                                   stroke_color=watermark_stroke_color,
                                                   stroke_width=watermark_stroke_width,
                                                   back_rect=watermark_back_react, rect_stroke=watermark_rect_stroke,
                                                   rect_transparency=watermark_rect_transparency,
                                                   back_rect_color=watermark_back_rect_color,
                                                   back_rect_outline_color=watermark_back_rect_outline_color)
            watermark_image = watermark_image.set_start(0).set_duration(voice_duration).set_fps(watermark_fps)\
                .set_position("center", "center")
            image_clips.append(watermark_image)

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
        final_processed_video.write_videofile(f"{output_location}.mp4")

    else:
        print(f"Sorry something wrong with the number {script_number} script")


if __name__ == "__main__":
    pass








