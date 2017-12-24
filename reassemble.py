#!/usr/bin/python

from Queue import Queue
from threading import Thread
import os
import re
import sys

files = [f for f in os.listdir('./files') if os.path.isfile('./files/'+f)]
bbox_lat_min =  sys.maxint
bbox_lat_max = -sys.maxint
bbox_lon_min =  sys.maxint
bbox_lon_max = -sys.maxint

for f in files:
	match = re.search('([0-9]{5})_([0-9]{5}).jpg',f)
	if match:
		lat = int(match.group(1))
		lon = int(match.group(2))
		bbox_lat_max = max( lat, bbox_lat_max );
		bbox_lat_min = min( lat, bbox_lat_min );
		bbox_lon_max = max( lon, bbox_lon_max );
		bbox_lon_min = min( lon, bbox_lon_min );

print "BBOX:"
print bbox_lon_min,bbox_lon_max
print bbox_lat_min,bbox_lat_max

from PIL import Image

def do_stuff(q):
  while True:
	(f) = q.get()
	match = re.search('([0-9]{5})_([0-9]{5}).jpg',f)
	if match:
		lat = int(match.group(1))-bbox_lat_min
		lon = int(match.group(2))-bbox_lon_min
		left  = rescale * lon
		up    = rescale * lat
		source = Image.open(f).convert("RGBA")
		source.thumbnail((rescale,rescale))
		im.paste(source,(left,up))
		source.close();
	q.task_done()

q = Queue(maxsize=100)
num_threads = 4

for i in range(num_threads):
	worker = Thread(target=do_stuff, args=(q,))
	worker.daemon = True
	worker.start()

rescale = 4
res_lat = rescale * (bbox_lat_max - bbox_lat_min + 1)
res_lon = rescale * (bbox_lon_max - bbox_lon_min + 1)
print "Creating new "+str(res_lon)+"x"+str(res_lat)+" image"
im = Image.new("RGB",(res_lon,res_lat))
print im
for i in xrange(1,len(files)):
	f = './files/'+files[i]
	q.put( f )
q.join()
im.save("bitmap_out2.png")
im.close()

