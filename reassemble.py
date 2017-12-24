#!/usr/bin/python

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
w = 1 + bbox_lon_max - bbox_lon_min
h = 1 + bbox_lat_max - bbox_lat_min
print "Creating new "+str(w)+"x"+str(h)+" image"
im = Image.new("RGB",(w,h))
print im
for i in xrange(1,len(files)):
	f = files[i]
	match = re.search('([0-9]{5})_([0-9]{5}).jpg',f)
	if match:
		lat = int(match.group(1))-bbox_lat_min
		lon = int(match.group(2))-bbox_lon_min
		im.putpixel((lon,lat), (255,255,255))
im.save("bitmap.png")
im.close()

rescale = 8
res_lat = rescale * (bbox_lat_max - bbox_lat_min + 1)
res_lon = rescale * (bbox_lon_max - bbox_lon_min + 1)
print "Creating new "+str(res_lon)+"x"+str(res_lat)+" image"
im = Image.new("RGB",(res_lon,res_lat))
print im
for i in xrange(1,len(files)):
	print i,len(files)
	f = './files/'+files[i]
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
im.save("bitmap_out.png")
im.close()

res_lat = 512 * (bbox_lat_max - bbox_lat_min + 1)
res_lon = 512 * (bbox_lon_max - bbox_lon_min + 1)
print "Creating new "+str(res_lon)+"x"+str(res_lat)+" image"
#im = Image.new("RGB",(res_lon,res_lat))
for i in xrange(1,len(files)):
	f = './files/'+files[i]
	match = re.search('([0-9]{5})_([0-9]{5}).jpg',f)
	if match:
		lat = int(match.group(1))
		lon = int(match.group(2))
		left  = 512 * ( lon - bbox_lon_max );
		up    = 512 * ( lat - bbox_lat_max );
		source = Image.open(f).convert("RGBA");
		im.paste(source,(left,up))
		print source
		source.close();

im.save("output.png")
