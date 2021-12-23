import cv2
import numpy as np
# from numba import jit

# @jit(nopython=True)

# img_raw = cv2.imread('tmpaa6y9sih.PNG')
# img_raw.show()



def targetLocateMul(npimg):
    npimg = cv2.cvtColor(npimg, cv2.COLOR_RGB2BGR)


    maxArea=200
    edge=10
    tmp=npimg.copy()

    hsv = cv2.cvtColor(npimg, cv2.COLOR_BGR2HSV) 
    lower = np.array([4, 43, 46])  
    upper = np.array([34, 255, 255]) 
    orange = cv2.inRange(hsv, lowerb=lower, upperb=upper)
    contours, hierarchy = cv2.findContours(
        orange,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_NONE)
    g_dConArea = []
    for i in contours:
        g_dConArea.append(cv2.contourArea(i))

    max_area_index = 0
    max_area = maxArea
    for i in range(len(g_dConArea)):
        # print(g_dConArea[i])
        if g_dConArea[i] > max_area:
            max_area_index = i
            max_area = g_dConArea[i]

    if max_area == maxArea:
        res = targetLocateRed(tmp)
        if res == None:
            return None,None
        else:
            return res, 3



    (x, y), radius = cv2.minEnclosingCircle(contours[max_area_index])
    center = [int(x), int(y)]
    radius = int(radius)
    # print(radius)
    cv2.circle(orange, center, radius, (0, 200, 255), 10)
    cv2.circle(npimg, center, radius, (0, 0, 255), 10)
    cv2.imwrite("thrimg.jpg", orange)
    cv2.imwrite("img.jpg", npimg)


    if center[0] > edge and center[1]>edge and radius>200:
        print('orange')

        return center, 1
    elif center[0] > edge and center[1]>edge and radius<200:
        print('longan')

        return center, 2
    else:
        return None,None
        

# def targetLocateYellow(npimg):
#     global maxArea,edge

#     hsv = cv2.cvtColor(npimg, cv2.COLOR_BGR2HSV)
#     lower = np.array([26, 43, 46])  
#     upper = np.array([34, 255, 255])
#     yellow = cv2.inRange(hsv, lowerb=lower, upperb=upper)
#     contours, hierarchy = cv2.findContours(
#         yellow,
#         cv2.RETR_LIST,
#         cv2.CHAIN_APPROX_NONE)
#     g_dConArea = []
#     for i in contours:
#         g_dConArea.append(cv2.contourArea(i))

#     max_area_index = 0
#     max_area = maxArea
#     for i in range(len(g_dConArea)):
#         # print(g_dConArea[i])
#         if g_dConArea[i] > max_area:
#             max_area_index = i
#             max_area = g_dConArea[i]

#     if max_area == maxArea:
#         return None

#     (x, y), radius = cv2.minEnclosingCircle(contours[max_area_index])
#     center = [int(x), int(y)]
#     radius = int(radius)
#     cv2.circle(yellow, center, radius, (0, 200, 255), 10)
#     cv2.circle(npimg, center, radius, (0, 0, 255), 10)
#     cv2.imwrite("thrimg.jpg", yellow)
#     cv2.imwrite("img.jpg", npimg)


#     if center[0] > edge and center[1]>edge:
#         return center
#     else:
#         return None

def targetLocateRed(npimg):
    # print('red')
    maxArea=200
    edge=10

    hsv = cv2.cvtColor(npimg, cv2.COLOR_BGR2HSV) 

    lower = np.array([150, 55, 57]) 
    upper = np.array([180, 255, 255]) 
    red = cv2.inRange(hsv, lowerb=lower, upperb=upper)

    contours, hierarchy = cv2.findContours(
        red,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_NONE)
    g_dConArea = []
    for i in contours:
        g_dConArea.append(cv2.contourArea(i))

    max_area_index = 0
    max_area = maxArea
    for i in range(len(g_dConArea)):
        # print(g_dConArea[i])
        if g_dConArea[i] > max_area:
            max_area_index = i
            max_area = g_dConArea[i]

    if max_area == maxArea:
        return None

    (x, y), radius = cv2.minEnclosingCircle(contours[max_area_index])
    center = [int(x), int(y)]
    radius = int(radius)
    cv2.circle(red, center, radius, (0, 200, 255), 10)
    cv2.circle(npimg, center, radius, (0, 0, 255), 10)


    cv2.imwrite("thrimg.jpg", red)
    cv2.imwrite("img.jpg", npimg)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    if center[0] > edge and center[1]>edge:
        return center
    else:
        return None


def target_locate(img):
    # cv2.imwrite('haha.png',img)
    maxArea=200
    edge=10

    b, g, r = cv2.split(img)
    # g = cv2.GaussianBlur(g, (15, 15), 0)
    # ret, g = cv2.threshold(g, 150, 255, cv2.THRESH_BINARY)
    # cv2.imwrite("g.jpg", g)

    # r = cv2.GaussianBlur(r, (15, 15), 0)
    # ret, r = cv2.threshold(r, 150, 255, cv2.THRESH_BINARY)
    # cv2.imwrite("r.jpg", r)
    r = cv2.GaussianBlur(r, (15, 15), 0)
    # cv2.imwrite("origin.jpg", r)
    ret, r = cv2.threshold(r, 25, 255, cv2.THRESH_BINARY)
    # cv2.imwrite("threshould.jpg", r)

# g = cv2.GaussianBlur(b, (15, 15), 0)
# print(g)
# ret, g = cv2.threshold(g, 30, 255, cv2.THRESH_BINARY)

    # b_find(b, g, r)
    # img_threshold = r
    img_threshold = r
    # img_threshold = cv2.GaussianBlur(img_threshold, (15, 15), 0)
    # ret, img_threshold = cv2.threshold(img_threshold, 70, 255, cv2.THRESH_BINARY)


    # cv2.imwrite("thrimg.jpg", img_threshold)
    contours, hierarchy = cv2.findContours(
        img_threshold,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_NONE)
    g_dConArea = []
    for i in contours:
        g_dConArea.append(cv2.contourArea(i))

    max_area_index = 0
    max_area = maxArea
    for i in range(len(g_dConArea)):
        print(g_dConArea[i])
        if g_dConArea[i] > max_area:
            max_area_index = i
            max_area = g_dConArea[i]

    if max_area == maxArea:
        return  None

    (x, y), radius = cv2.minEnclosingCircle(contours[max_area_index])
    center = [int(x), int(y)]
    radius = int(radius)
    cv2.circle(img_threshold, center, radius, (155, 155, 155), 10)
    cv2.circle(img, center, radius, (155, 155, 155), 10)
    cv2.imwrite("thrimg.jpg", img_threshold)
    cv2.imwrite("img.jpg", img)


    if center[0] > edge and center[1]>edge:
        return center
    else:
        return None




# def main():
#     # print(target_locate(takePhoto()))


# if __name__ == "__main__":
#     main()
