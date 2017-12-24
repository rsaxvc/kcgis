#! /usr/bin/python

from Queue import Queue
from threading import Thread
import requests
import os

sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)
sess.mount('http://maps2.kcmo.org', adapter)

def do_stuff(q):
  while True:
	(x,y) = q.get()
	outpath = "files/"+str(x)+"_"+str(y)+".jpg"
	if( not os.path.isfile(outpath) ):
		item = "http://maps2.kcmo.org/kcgis/rest/services/external/Orthophoto_2016/MapServer/tile/10/"+str(x)+"/"+str(y)
		try:
			resp = sess.get(item,timeout=5)
			if( resp.status_code == requests.codes.ok ):
				file = open(outpath, "w")
				file.write(resp.content)
				file.close()
				print "Downloaded "+outpath
			else:
				print "Failed to download "+str(x)+","+str(y)
		except requests.exceptions.ConnectionError as errc:
			print ("Error Connecting:",errc)
		except requests.exceptions.Timeout:
			print ("Timeout Error:",errt)
		except requests.exceptions.RequestException as err:
			print ("OOps: Something Else",err)
	else:
		print "Using cached "+outpath
	q.task_done()

q = Queue(maxsize=0)
num_threads = 20

for i in range(num_threads):
	worker = Thread(target=do_stuff, args=(q,))
	worker.daemon = True
	worker.start()

tiles = []
for x in xrange(83309,84183):
	for y in xrange(82656,83177):
		tiles.append( (x,y) )
from random import shuffle
shuffle(tiles)
for t in tiles:
	q.put( t )

#for x in xrange(83386,83599):
#	for y in xrange(82900,83000):
#		q.put((x,y))
#for x in xrange(83386,83599):
#	for y in xrange(82700,82600,-1):
#		q.put((x,y))
#for x in xrange(83386,83599):
#	for y in xrange(82750,82900):
#		q.put((x,y))

q.join()

