# bbb-export

This project is based on [createwebinar/bbb-download](https://github.com/createwebinar/bbb-download).
In the original project you are only able to see the presentation and the extracted audio.
This project shows the presentation (Important! No wideboard functions besides zooming) 
and the webcams of all participants stacked up next it. The video height is now 1280 pixel, 
whereas the width is variable.


## Requirements

- python3
- ffmpeg compiled with libx264 support

## Usage

Specify in `ffmpeg.py` the variable `FFMPEG` with the location of ffmpeg.

`python3 download.py meeting_id`

The video will be at the folder `/var/bigbluebutton/published/presentation/<meeting_id>/output.mp4`