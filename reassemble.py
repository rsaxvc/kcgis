#!/usr/bin/python3

import queue
from threading import Thread
import os
import re
import sys
import psutil

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--minlat', help='minimum latitude in block offsets')
parser.add_argument('--minlon', help='minimum longitude in block offsets')
parser.add_argument('--maxlat', help='maximum latitude in block offsets')
parser.add_argument('--maxlon', help='maximum longitude in block offsets')
args = parser.parse_args()

files = [f for f in os.listdir('./files') if os.path.isfile('./files/'+f)]
bbox_lat_min =  sys.maxsize
bbox_lat_max = -sys.maxsize
bbox_lon_min =  sys.maxsize
bbox_lon_max = -sys.maxsize

for f in files:
	match = re.search('([0-9]{5})_([0-9]{5}).jpg',f)
	if match:
		lat = int(match.group(1))
		lon = int(match.group(2))
		bbox_lat_max = max( lat, bbox_lat_max );
		bbox_lat_min = min( lat, bbox_lat_min );
		bbox_lon_max = max( lon, bbox_lon_max );
		bbox_lon_min = min( lon, bbox_lon_min );

if args.minlat != None:
	bbox_lat_min = int(args.minlat)
if args.minlon != None:
	bbox_lon_min = int(args.minlon)
if args.maxlat != None:
	bbox_lat_max = int(args.maxlat)
if args.maxlon != None:
	bbox_lon_max = int(args.maxlon)

print ("BBOX LON:",bbox_lon_min,bbox_lon_max)
print ("BBOX LAT:",bbox_lat_min,bbox_lat_max)

from PIL import Image

def do_stuff(q):
	while True:
		(f) = q.get()
		match = re.search('([0-9]{5})_([0-9]{5}).jpg',f)
		if match:
			lat = int(match.group(1))-bbox_lat_min
			lon = int(match.group(2))-bbox_lon_min
			if lat >= 0 and lat <= bbox_lat_max - bbox_lat_min and lon >= 0 and lon <= bbox_lon_max - bbox_lon_min:
				left  = rescale * lon
				up    = rescale * lat
				source = Image.open(f).convert("RGBA")
				source.thumbnail((rescale,rescale))
				im.paste(source,(left,up))
				source.close();
		q.task_done()

q = queue.Queue(maxsize=psutil.cpu_count())
for i in range(psutil.cpu_count()):
	worker = Thread(target=do_stuff, args=(q,))
	worker.daemon = True
	worker.start()

#Render image
dlat = bbox_lat_max - bbox_lat_min + 1
dlon = bbox_lon_max - bbox_lon_min + 1
print ("Source image is "+str(dlon*512)+"x"+str(dlat*512))
#512x is the base tile resolution
#However, the full city takes a lot of RAM to do,
#so downscale each tile to width,height=rescale,rescale
rescale = 64
res_lat = rescale * dlat
res_lon = rescale * dlon
im = Image.new("RGB",(res_lon,res_lat))
nFiles = len(files)
threshold = 0.0
for i in range(1,len(files)):
	pct = float(i)/nFiles
	if pct > threshold:
		print ('Parsing Images ({0}%)\r'.format(int(100*pct)),)
		sys.stdout.flush()
		threshold += 0.01;
	q.put( './files/'+files[i] )
q.join()
while( rescale > 0 ):
	print ("Rescaling to "+str(dlon*rescale)+"x"+str(dlat*rescale))
	im.save("bitmap_"+str(rescale)+".png")
	rescale //= 2
	sz = im.size
	im.thumbnail((im.size[0]/2,im.size[1]/2))
im.close()

