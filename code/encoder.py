import matplotlib.pyplot as plt
import scipy.ndimage as ndi
from PIL import Image
import numpy as np
import string
import sys 
import os

units = list(string.printable)[0:-7]
r = '\033[31m'; g = '\033[32m'; b = '\033[34m'
c = '\033[36m'; m = '\033[31m'; y = '\033[33m'
k = '\033[37m'; w = '\033[39m'
colors = {str([1,0,0]):r, str([0,1,0]):g, str([0,0,1]):b,
		  str([0,1,1]):c, str([1,0,1]):m, str([1,1,0]):y,
		  str([0,0,0]):k, str([1,1,1]):w}

k1 = [[-1,2,-1],
	  [ 2,3, 2],
	  [-1,2,-1]]

def ind2sub(dims):
    subs = []
    ii = 0
    table = {}
    for x in range(dims[0]):
        for y in range(dims[1]):
            table[ii] = [x, y]
            ii +=1
    return table

def resize_img(name):
	sz =  int(os.popen("stty size","r").read().split()[1])/2 - 10
	img = Image.open(name)
	img.thumbnail((sz, sz), Image.ANTIALIAS)
	return np.array(img).astype(np.uint8)

def pre_process(img_name):
	img_in = np.array(plt.imread(img_name))
	if img_in.shape[0] > 60 or img_in.shape[1] > 60:
		img_in = resize_img(img_name)
	if len(img_in.shape)==3:
		 bw = np.zeros((img_in.shape[0],img_in.shape[1]))
		 bw[:,:] = np.array(img_in[:,:,0]/3+img_in[:,:,1]/3+img_in[:,:,2]/3).astype(np.uint8)
	elif len(img_in.shape)==2:
		bw = img_in
	else:
		print('[!!] Image shape cannot be processed')
		exit()
	return bw, img_in

def im2ascii(bw, im, nE, nC):
	# Edge Detection1
	kernel = np.array([[0, -1*nE, 0],
	                   [-1*nE, nC, -1*nE],
	                   [0, -1*nE, 0]])
	# Determine how to map ascii
	crange = len(units)
	abs_max = np.max(bw)
	abs_min = np.min(bw)
	mean = np.mean(bw)
	meanc= np.mean(im)
	# Need to map printable chars to bw range
	bw = ndi.convolve(bw,kernel)
	# bw = bw[:,:] - mean
	bitval = np.array(np.linspace(abs_min,abs_max,crange)).astype(np.uint8)
	out = ''
	ind = 0
	lut = ind2sub(bw.shape)
	for row in bw:
		for v in row:
			[x,y] = lut[ind]
			k = str(np.array(im[x,y,:] > meanc).astype(np.int)).replace(' ',', ')
			if k in colors.keys():
				c = colors[k]
				if np.max(bw[x,y]) == abs_max:
					out += '\033[1m'
				out += c+units[int(v/crange-1)] + '.'+'\033[0m'
			ind += 1
		if len(row):
			out += '\n'
	return out


def check_args():
	if len(sys.argv) < 2:
		print('[!] Usage: python encoder.py [image/video]')
		exit()
	# Determine if image or video
	f = sys.argv[-1]
	ext = f.split('.')[-1]
	img_types = ['jpeg','jpg','png']
	vid_types = ['gif','mp4','avi']
	
	if ext in img_types:
		# Load Image and Pre-process it
		bw_im, img = pre_process(sys.argv[1])
		data = im2ascii(bw_im, img, 3,1)
		print(data)
		
	elif ext in vid_types:
		# Break into many images and process one by one
		if os.path.isdir('frames'):
			os.system('rm -rf frames')
		os.mkdir('frames')
		os.system('ffmpeg -i '+f+" frames/out%03d.jpg")
		# Process Each Frame and print to terminal
		N = len(os.listdir('frames'))
		print('[+] Processing %d Frames' % N)
		for i in range(1,N):
			bw, im = pre_process('frames/out%03d.jpg' % i)
			print(im2ascii(bw,im,3,3))
			# time.sleep(.05)
			# os.system('clear')
		os.system('rm -rf frames')


def main():
	# Check input Args
	check_args()
	if not os.path.isfile(sys.argv[1]):
		print('[!!] Cannot find %s' % sys.argv[1])
		exit()


	

if __name__ == '__main__':
	main()