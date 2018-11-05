# BSPlayer Subtitles Downloader
![alt-text](http://bsplayer.com/media/images/logo.png)
### Intro
BSPlayer is a great media player that automatically downloads subtitles for the video you are watching.
I often find myself needing to download subtitles for many videos at once.
To do that, I usually open each video file at a time using BSPlayer, wait for the subtitles to be downloaded and proceed to the next file.
This method is really time consuming, and I just knew that I could do better.

Ladies and gentlemen, I'm proud to present you the "BSPlayer Subtitles Downloader"!
This is a script that receives the video file path, and simply downloads the subtitles for it just like BSPlayer does.
Behind the scenes, the script uses a nice Python API I implemented to interact with the BSPlayer subtitles server.
I implemented this API by analyzing the HTTP requests BSPlayer was making to the subtitles server, using Wireshark. I also got a little help from the nice repository I found: `service.subtitles.bsplayer`.

I also wrote a script that adds a nice Windows context menu button, which allows you to right click for `Download Subtitles`.

The API is completely open source, so feel free to use it :)

### External Links:
- http://bsplayer.com/
- https://github.com/realgam3/service.subtitles.bsplayer