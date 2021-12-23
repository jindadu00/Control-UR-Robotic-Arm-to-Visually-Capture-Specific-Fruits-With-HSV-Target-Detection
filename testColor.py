from target_locate import *

npimg=cv2.imread('3.bmp')
print(targetLocateMul(npimg))
img=cv2.imread('thrimg.jpg')
cv2.imshow('longan.png',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
