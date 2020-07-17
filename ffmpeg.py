import os

FFMPEG = '/opt/ffmpeg/ffmpeg'
VID_ENCODER = 'libx264'


def make_mp4(video_file, out_file):
    command = '%s -i %s -c:v libx264 %s -y' % (
        FFMPEG, video_file, out_file)
    os.system(command)


def scale_fixed(video_file, out_file):
    command = '%s -i %s -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1" -c:v libx264 -max_muxing_queue_size 1024  %s -y' % (
        FFMPEG, video_file, out_file)
    os.system(command)


def scale_height(height, video_file, out_file):
    command = '%s -i %s -vf scale=-2:%s %s -y' % (
        FFMPEG, video_file, str(height), out_file)
    os.system(command)


def concat_presentation_webcam(presentation_file, webcam_file, out_file):
    command = '%s -i %s -i %s -max_muxing_queue_size 1024 -c:v libx264 -filter_complex hstack -r 24 %s -y' % (
        FFMPEG, presentation_file, webcam_file, out_file)
    os.system(command)


def mux_slideshow_audio(video_file, audio_file, out_file):
    command = '%s -i %s -i %s -map 0 -map 1 -codec copy -shortest %s' % (
        FFMPEG, video_file, audio_file, out_file)
    os.system(command)


def extract_audio_from_video(video_file, out_file):
    command = '%s -i %s -ab 160k -ac 2 -ar 44100 -vn %s' % (FFMPEG, video_file, out_file)
    os.system(command)


def create_video_from_image(image, duration, out_file):
    command = '%s -loop 1 -r 5 -f image2 -i %s -c:v %s -t %s -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" %s' % (
        FFMPEG, image, VID_ENCODER, duration, out_file)
    os.system(command)


def concat_videos(video_list, out_file):
    command = '%s -y -f concat -safe 0 -i %s -c copy %s' % (FFMPEG, video_list, out_file)
    os.system(command)


def mp4_to_ts(input, output):
    command = '%s -i %s -c copy -bsf:v h264_mp4toannexb -f mpegts %s' % (FFMPEG, input, output)
    os.system(command)


def concat_ts_videos(input, output):
    command = '%s -i %s -c copy -bsf:a aac_adtstoasc %s' % (FFMPEG, input, output)
    os.system(command)


def rescale_image(image, height, width, out_file):
    if height < width:
        command = '%s -i %s -vf pad=%s:%s:0:oh/2-ih/2 %s -y ' % (FFMPEG, image, width, height, out_file)
    else:
        command = '%s -i %s -vf pad=%s:%s:0:ow/2-iw/2 %s -y ' % (FFMPEG, image, width, height, out_file)

    os.system(command)


def trim_video(video_file, start, end, out_file):
    start_h = start / 3600
    start_m = start / 60 - start_h * 60
    start_s = start % 60

    end_h = end / 3600
    end_m = end / 60 - end_h * 60
    end_s = end % 60

    str1 = '%d:%d:%d' % (start_h, start_m, start_s)
    str2 = '%d:%d:%d' % (end_h, end_m, end_s)
    command = '%s -ss %s -t %s -i %s -vcodec copy -acodec copy %s' % (FFMPEG, str1, str2, video_file, out_file)
    os.system(command)


def trim_video_by_seconds(video_file, start, end, out_file):
    command = '%s -ss %s -i %s -c copy -t %s %s' % (FFMPEG, start, video_file, end, out_file)
    os.system(command)


def trim_audio(audio_file, start, end, out_file):
    temp_file = 'temp.mp3'
    start_h = start / 3600
    start_m = start / 60 - start_h * 60
    start_s = start % 60

    end_h = end / 3600
    end_m = end / 60 - end_h * 60
    end_s = end % 60

    str1 = '%d:%d:%d' % (start_h, start_m, start_s)
    str2 = '%d:%d:%d' % (end_h, end_m, end_s)
    command = '%s -ss %s -t %s -i %s %s' % (FFMPEG, str1, str2, audio_file, temp_file)
    os.system(command)
    mp3_to_aac(temp_file, out_file)
    os.remove(temp_file)


def trim_audio_start(dictionary, length, full_audio, audio_trimmed):
    times = dictionary.keys()
    times.sort()
    trim_audio(full_audio, int(round(times[0])), int(length), audio_trimmed)


def trim_video_start(dictionary, length, full_vid, video_trimmed):
    times = dictionary.keys()
    times.sort()
    trim_video(full_vid, int(round(times[2])), int(length), video_trimmed)


def mp3_to_aac(mp3_file, aac_file):
    command = '%s -i %s -c:a libfdk_aac %s' % (FFMPEG, mp3_file, aac_file)
    os.system(command)


def webm_to_mp4(webm_file, mp4_file):
    command = '%s -i %s -qscale 0 %s' % (FFMPEG, webm_file, mp4_file)
    os.system(command)
