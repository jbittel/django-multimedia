"""
A management command which pulls rss feeds for each feed setup in the feedreader.Feed.
"""
import os
import shutil
from dateutil import parser
from subprocess import Popen, PIPE
from django.core.management.base import NoArgsCommand
from django.utils.html import strip_tags
from django.conf import settings
from multimedia.models import Video
from multimedia.utils import upload_file, check_encoded_video_length

class Command(NoArgsCommand):
    help = "Pull all new entries from all Feed records"

    def handle_noargs(self, **options):        
        videos = Video.objects.filter(uploaded=False)
        for video in videos:
            print "Encoding and Uploading %s" % video
            video_path = os.path.join(settings.MEDIA_ROOT, video.file.name)
            if os.path.exists(video_path):
                need_to_encode = True
                encoded_video_path = os.path.join(settings.MEDIA_ROOT, "%s_encoded.f4v" % video.file.name)
                if os.path.exists(encoded_video_path):
                    if check_encoded_video_length(video):
                        print "No need to encode"
                        need_to_encode = False
                    else:
                        print "Existing encoded version is bad, deleting and starting again"
                        os.remove(encoded_video_path)
                    
                if need_to_encode:
                    temp_video_path = "%s.encoding" % video_path
                    shutil.move(video_path, temp_video_path)
                    command = '/usr/local/bin/ffmpeg -i %s -f mp4 -acodec libfaac -ab 128k -vcodec libx264 -vpre slow -b 690k -ac 2 -crf 22 -s 496x278 %s' % (temp_video_path, encoded_video_path)
                    process = Popen(command.split(' '))
                    process.wait()
                    #log_file = open('/tmp/video_encode_log_%s.txt' % video.id, 'w')
                    #log_file.write(process.communicate()[0])
                    #log_file.close()
                    shutil.move(temp_video_path, video_path)
                
                # We only want to do this for the first video file that isn't already being encoded, that 
                # way we won't ever have multiple encoding processes trying to encode the same videos.
                upload_file(video)
                return 
                
