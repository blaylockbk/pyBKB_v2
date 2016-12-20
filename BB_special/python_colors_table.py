## Brian Blaylock
## 12 May 2016

# from: http://stackoverflow.com/questions/22408237/named-colors-in-matplotlib

# plot python colors for printing

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import math
import matplotlib
for name, hex in matplotlib.colors.cnames.iteritems():
    print(name, hex)
    
width= 8
height= 11

fig = plt.figure(figsize=(width,height))
ax = fig.add_subplot(111)

ratio = 1.0 / 3.0
count = math.ceil(math.sqrt(len(colors.cnames)))
print count
x_count = count * ratio
y_count = count / ratio
x = 0
y = 0
w = 1 / x_count
h = 1 / y_count

for c in sorted(colors.cnames):
    pos = (x / x_count, y / y_count)
    ax.add_patch(patches.Rectangle(pos, w, h, color=c))
    ax.annotate(c, xy=pos,fontsize=10)
    if y >= y_count-1:
        x += 1
        y = 0
    else:
        y += 1
        

plt.yticks([])
plt.xticks([])
plt.savefig('allcolors',bbox_inches='tight',dpi=300)
#plt.show()