from xml.dom import minidom
import sys
import os
import shutil
import ffmpeg
import re
import time

tmp = sys.argv[1].split('-')
try:
    if tmp[2] == 'presentation':
        meetingId = tmp[0] + '-' + tmp[1]
    else:
        sys.exit()
except IndexError:
    meetingId = sys.argv[1]

PATH = '/var/bigbluebutton/published/presentation/'
source_dir = PATH + meetingId + "/"
temp_dir = source_dir + 'temp/'
target_dir = source_dir + 'download/'
events_file = source_dir + 'shapes.svg'
source_events = '/var/bigbluebutton/recording/raw/' + meetingId + '/events.xml'
# Deskshare
SOURCE_DESKSHARE = source_dir + 'deskshare/deskshare.webm'
TMP_DESKSHARE_FILE = temp_dir + 'deskshare.mp4'


def extract_timings(bbb_version):
    doc = minidom.parse(events_file)
    dictionary = {}
    total_length = 0
    j = 0

    for image in doc.getElementsByTagName('image'):
        path = image.getAttribute('xlink:href')

        if j == 0 and '2.0.0' > bbb_version:
            path = u'/usr/local/bigbluebutton/core/scripts/logo.png'
            j += 1

        in_times = str(image.getAttribute('in')).split(' ')
        out_times = image.getAttribute('out').split(' ')

        temp = float(out_times[len(out_times) - 1])
        if temp > total_length:
            total_length = temp

        occurrences = len(in_times)
        for i in range(occurrences):
            dictionary[float(in_times[i])] = temp_dir + str(path)

    return dictionary, total_length


def create_slideshow(dictionary, length, result):
    video_list = 'video_list.txt'
    video_list_tmp = []
    video_list_fn = []
    f = open(video_list, 'w')

    times = list(dictionary.keys())
    times.sort()

    ffmpeg.webm_to_mp4(SOURCE_DESKSHARE, TMP_DESKSHARE_FILE)

    print("-=create_slideshow=-")
    for i, t in enumerate(times):
        tmp_name = '%d.mp4' % i
        tmp_ts_name = '%d.ts' % i
        image = dictionary[t]

        if i == len(times) - 1:
            duration = length - t
        else:
            duration = times[i + 1] - t

        out_file = temp_dir + tmp_name
        out_ts_file = temp_dir + tmp_ts_name

        if "deskshare.png" in image:
            print(sys.stderr, (0, i, t, duration))
            ffmpeg.trim_video_by_seconds(TMP_DESKSHARE_FILE, t, duration, out_file)
            ffmpeg.mp4_to_ts(out_file, out_ts_file)
        else:
            print(sys.stderr, (1, i, t, duration))
            ffmpeg.create_video_from_image(image, duration, out_ts_file)
        video_list_fn.append(out_ts_file)
        f.write('file ' + out_ts_file + '\n')
        video_list_tmp.append(out_ts_file)
    f.close()
    height = 1080
    # Scale video files
    with open(video_list, 'w') as f:
        for entry in video_list_fn:
            out_file = temp_dir + entry.split('/')[-1].split('.')[0] + '_new.ts'
            ffmpeg.scale_fixed(entry, out_file)
            f.write('file ' + out_file + '\n')
    ffmpeg.concat_videos(video_list, result)
    return height


def get_presentation_dims(presentation_name):
    doc = minidom.parse(events_file)
    images = doc.getElementsByTagName('image')

    for el in images:
        name = el.getAttribute('xlink:href')
        pattern = presentation_name
        if re.search(pattern, name):
            height = int(el.getAttribute('height'))
            width = int(el.getAttribute('width'))
            return height, width


def rescale_presentation(new_height, new_width, dictionary, bbb_version):
    times = list(dictionary.keys())
    times.sort()
    for i, t in enumerate(times):
        if i < 1 and '2.0.0' > bbb_version:
            continue
        ffmpeg.rescale_image(dictionary[t], new_height, new_width, dictionary[t])


def check_presentation_dims(dictionary, dims, bbb_version):
    names = dims.keys()
    heights = []
    widths = []

    for i in names:
        temp = dims[i]
        heights.append(temp[0])
        widths.append(temp[1])

    height = max(heights)
    width = max(widths)

    print("MAX Height:" + str(height))

    dim1 = height % 2
    dim2 = width % 2

    new_height = height
    new_width = width

    if dim1 or dim2:
        if dim1:
            new_height += 1
        if dim2:
            new_width += 1

    rescale_presentation(new_height, new_width, dictionary, bbb_version)


def prepare(bbb_version):
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    shutil.copytree("presentation", temp_dir + "presentation")
    dictionary, length = extract_timings(bbb_version)
    print("dictionary")
    print(dictionary)
    print("length")
    print(length)
    dims = get_different_presentations(dictionary)
    print("dims")
    print(dims)
    check_presentation_dims(dictionary, dims, bbb_version)
    return dictionary, length, dims


def get_different_presentations(dictionary):
    times = dictionary.keys()
    print("times")
    print(times)
    presentations = []
    dims = {}
    for t in times:
        name = dictionary[t].split("/")[7]
        print("name")
        print(name)
        if name not in presentations:
            presentations.append(name)
            dims[name] = get_presentation_dims(name)

    return dims


def cleanup():
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)


def bbbversion():
    bbb_ver = 0
    s_events = minidom.parse(source_events)
    for event in s_events.getElementsByTagName('recording'):
        bbb_ver = event.getAttribute('bbb_version')
    return bbb_ver


def main():
    print("\n<-------------------" + time.strftime("%c") + "----------------------->\n")

    bbb_version = bbbversion()
    print("bbb_version: " + bbb_version)

    os.chdir(source_dir)
    dictionary, length, dims = prepare(bbb_version)

    slideshow = source_dir + 'slideshow.mp4'

    try:
        height = create_slideshow(dictionary, length, slideshow)
        if os.path.isfile(source_dir + 'video/webcams.webm') and not os.path.isfile(source_dir + 'video/webcams.mp4'):
            ffmpeg.make_mp4(source_dir + 'video/webcams.webm', source_dir + 'video/webcams.mp4')
        ffmpeg.scale_height(height, source_dir + 'video/webcams.mp4', source_dir + 'video/webcams_new.mp4')
        ffmpeg.concat_presentation_webcam(slideshow, source_dir + 'video/webcams_new.mp4', source_dir + 'output.mp4')
    finally:
        print(sys.stderr, "Cleaning up temp files...")
        cleanup()
        print(sys.stderr, "Done")


if __name__ == "__main__":
    main()
