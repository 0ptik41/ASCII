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
colors = {str([1,0,0]):r,
		  str([0,1,0]):g,
		  str([0,0,1]):b,
		  str([0,1,1]):c,
		  str([1,0,1]):m,
		  str([1,1,0]):y,
		  str([0,0,0]):k,
		  str([1,1,1]):w}

k1 = [[-1,2,-1],
	 [2,3,2],
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

def main():

	if len(sys.argv) > 1:
		if not os.path.isfile(sys.argv[1]):
			print('[!!] Cannot find %s' % sys.argv[1])
			exit()
		img_in = np.array(plt.imread(sys.argv[1]))
		if img_in.shape[0] > 60 or img_in.shape[1] > 60:
			img = Image.open(sys.argv[1])
			img.thumbnail((40, 40), Image.ANTIALIAS)
			img_in = np.array(img).astype(np.uint8)
		if len(img_in.shape)==3:
			 bw = np.zeros((img_in.shape[0],img_in.shape[1]))
			 bw[:,:] = np.array(img_in[:,:,0]/3+img_in[:,:,1]/3+img_in[:,:,2]/3).astype(np.uint8)
		elif len(img_in.shape)==2:
			bw = img_in
		crange = len(units)
		abs_max = np.max(bw)
		abs_min = np.min(bw)
		mean = np.mean(bw)
		meanc= np.mean(img_in)
		# Need to map printable chars to bw range
		bw = bw[:,:] - mean
		bitval = np.array(np.linspace(abs_min,abs_max,crange)).astype(np.uint8)
		out = ''
		ind = 0
		lut = ind2sub(bw.shape)
		bw = ndi.convolve(bw,k1)
		for row in bw:
			for v in row:
				[x,y] = lut[ind]
				k = str(np.array(img_in[x,y,:] > meanc).astype(np.int)).replace(' ',', ')
				if k in colors.keys():
					c = colors[k]
					if np.max(bw[x,y]) == abs_max:
						out += '\033[1m'
					out += c+units[int(v/crange-1)] + '.'+'\033[0m'
				ind += 1
			out += '\n'
		print(out)

if __name__ == '__main__':
	main()
