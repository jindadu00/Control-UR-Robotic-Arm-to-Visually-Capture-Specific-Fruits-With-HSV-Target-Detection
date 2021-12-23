'''备注：
程序中的加速度都可以修改'''
from numpy.core.fromnumeric import reshape
import rtde_control
import rtde_receive
import rtde_io
import time
import numpy as np
import pandas as pd
import cv2
import gxipy as gx
from PIL import Image
from target_locate import *

def takePhoto():
    # create a device manager
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()
    if dev_num is 0:
        print("Number of enumerated devices is 0")
        return

    # open the first device
    cam = device_manager.open_device_by_index(1)

    # exit when the camera is a mono camera
    if cam.PixelColorFilter.is_implemented() is False:
        print("This sample does not support mono camera.")
        cam.close_device()
        return

    # set continuous acquisition
    cam.TriggerMode.set(gx.GxSwitchEntry.OFF)

    # set exposure
    cam.ExposureTime.set(10000.0)

    # set gain
    cam.Gain.set(10.0)

    # get param of improving image quality
    if cam.GammaParam.is_readable():
        gamma_value = cam.GammaParam.get()
        gamma_lut = gx.Utility.get_gamma_lut(gamma_value)
    else:
        gamma_lut = None
    if cam.ContrastParam.is_readable():
        contrast_value = cam.ContrastParam.get()
        contrast_lut = gx.Utility.get_contrast_lut(contrast_value)
    else:
        contrast_lut = None
    if cam.ColorCorrectionParam.is_readable():
        color_correction_param = cam.ColorCorrectionParam.get()
    else:
        color_correction_param = 0

    # start data acquisition
    cam.stream_on()

    # acquisition image: num is the image number
    num = 1
    for i in range(num):
        # get raw image
        raw_image = cam.data_stream[0].get_image()
        if raw_image is None:
            print("Getting image failed.")
            continue

        # get RGB image from raw image
        rgb_image = raw_image.convert("RGB")
        if rgb_image is None:
            continue

        # improve image quality
        rgb_image.image_improvement(
            color_correction_param, contrast_lut, gamma_lut)

        # create numpy array with data from raw image
        numpy_image = rgb_image.get_numpy_array()
        if numpy_image is None:
            continue

        # show acquired image
        img = Image.fromarray(numpy_image, 'RGB')
        # img.show()

    # stop data acquisition
    cam.stream_off()

    # close device
    cam.close_device()
    return img

def convert(uv):
    # internalMatrix=np.array([[0.0237,-0.9994,0.0268,61.9779],[0.9988,0.0248,0.0420,9.5602],[-0.0426,0.0258,0.9988,89.5939],[0,0,0,1]])
    # intrinsicMatrix=np.array([[5.4053,0,1.2561,0],[0,5.4041,0.9295,0],[0,0,0.001,0]])*1000

    df=pd.read_csv('HC2t.csv')
    internalMatrix=np.array(df)

    internalMatrix=np.linalg.inv(internalMatrix)

    df=pd.read_csv('Intrinsic.csv')
    intrinsicMatrix=np.array(df)

    vec=rtde_r.getActualTCPPose() 
    # vec=[1,1,1,0,0,1]
    T=np.array([vec[0],vec[1],vec[2]])
    rotVec=(vec[3],vec[4],vec[5])
    R,_ = cv2.Rodrigues(rotVec)
    A=np.zeros([4,4])
    A[0:3,0:3]=R
    A[0:3,3]=T
    A[3,3]=1

    S1=np.matmul(intrinsicMatrix,internalMatrix)
    S=np.matmul(S1,A)

    u=uv[0]
    v=uv[1]

    w=-0.03  #水果高度
    Z=0.55
    uv=np.array([u,v]).reshape(2,1)
    w1=np.array([w,1]).reshape(2,1)
    M1=S[0:2,0:2]
    M2=S[0:2,2:4]
    # print(M1)
    # print(M2)
    # print(S)
    A1=np.linalg.inv(M1)
    A2=uv*Z-np.matmul(M2,w1)
    return np.matmul(A1,A2)+np.array([0,1.126]).reshape(2,1)

global speed_move, detime
speed_move = 0.055  #传送带的速度
detime = 0.12  #设定想在多久内抓到这个东西（用于爪子已经在水果上方待命，在dettime时间内x方向和爪子相对静止，并且动Y轴，最后抓）
rtde_c = rtde_control.RTDEControlInterface("192.168.1.50")
rtde_r = rtde_receive.RTDEReceiveInterface("192.168.1.50")
rtde_ioz = rtde_io.RTDEIOInterface("192.168.1.50")


# print(rtde_r.getActualTCPPose())


# img=takePhoto()
# img=np.array(img)
# res=targetLocateRed(img)
# print(res)

# img=np.array(takePhoto())
# pixivCor=target_locate(img)
# worldCor=convert(pixivCor)
# print(pixivCor)
# print(worldCor)



global home,watch_place,dump_place #初始状态，观测状态，丢弃状态
home = [-0.54024799 ,0.07723357,  0.43712953 , 0.03770127, -3.09777475, -0.0425077]
#watch_place = [-0.2 , 0.5 , 0.5,  -0.001, -3.12, 0.04]
watch_place = [-0.20799560265204664, 0.5616711872011387, 0.573, 0.009887303513048881, 3.1325403604628073, 0.03842126312553712]

#dump_place = [-0.40398201 , -0.16100511 , 0.35000386,  0.03770127, -3.09777475, -0.0425077]
dump_place = home.copy()
#rtde_c.moveJ_IK(home, 2, 5)
time.sleep(0.001)
rtde_c.moveJ_IK(watch_place, 2, 5)
time.sleep(0.001)
rtde_ioz.setAnalogOutputVoltage(0, 0)



def grasp(speed, time3, target_pos=[-0.40398201 , 0.56100511 , 0.45000386,  0.03770127, -3.09777475, -0.0425077],flag=1):
    global home,watch_place,dump_place
    #抓取函数
    global detime
    first_pos = target_pos.copy()
    height = 0.07  #设定的抓取前达到的高度
    first_pos[2]+= height
    first_pos[0]+= speed*2
    rtde_c.moveJ_IK(first_pos, 2, 4) #达到水果上方
    while(time.time()-time3<2): #等待水果到达
        time.sleep(0.01)
    
    x_len = speed*(detime+0.12)
    speed_len = pow(height**2+x_len**2,0.5)/detime #计算抓取时的速度
    target_pos[0]+=x_len/2
    target_pos[2]+=height/2
    # target_pos[0]+=0.05
    rtde_c.moveL(target_pos,speed_len,10)
    target_pos[0]+=x_len/2
    target_pos[2]-=height/2
    rtde_ioz.setAnalogOutputVoltage(0, 0.12)
    rtde_c.moveL(target_pos,speed_len,10)#移动到和水果平行，下一步抓取即可
    target_pos[2]+=0.2
    time.sleep(0.2)
    rtde_c.moveJ_IK(target_pos,1,0.5)#向上移动以免爆炸
    time.sleep(0.1)

    if(flag==1):
        rtde_c.moveJ_IK(dump_place, 1, 1) #移动到丢弃地点
        rtde_ioz.setAnalogOutputVoltage(0, 0)
        time.sleep(0.1)

    elif(flag==2):
        dump_place2 = dump_place.copy()
        dump_place2[1] +=0.1
        rtde_c.moveJ_IK(dump_place2, 1, 1) #移动到丢弃地点_2
        rtde_ioz.setAnalogOutputVoltage(0, 0)
        time.sleep(0.1)
    else:
        dump_place2 = dump_place.copy()
        dump_place2[1] +=0.2
        rtde_c.moveJ_IK(dump_place2, 1, 1) #移动到丢弃地点_3
        rtde_ioz.setAnalogOutputVoltage(0, 0)
        time.sleep(0.1)



    rtde_c.moveJ_IK(watch_place, 1, 4) #移动到观测地点




posey_position = [0.14200386 , 0.03770127, -3.09777475, -0.0425077]
#预计抓取的姿态和z高度,轨道固定情况下则是固定值，预先设定
time1 = time.time()

while(time.time()-time1<60): #比赛尚未结束，假设比赛30s
    rtde_c.moveJ_IK(watch_place, 2, 4) #以最大速度和最大加速度回到初始位置（观测位置）

    #如果检测到轨道有水果，执行后面
    while True:
        time3 = time.time() #记录时间
        img=takePhoto()
        img=np.array(img)
        res, flag=targetLocateMul(img)
        if res is not None:
            break
    apple_position = convert(res)
    print(res)
    print(apple_position)
    #计算水果的位置

    #这一步从其他程序输入水果预计1S后到达的位置

    target_pos = watch_place.copy()
    target_pos[0:2] = apple_position
    target_pos[2:] = posey_position
    grasp(speed_move,time3,target_pos,flag) #完成一轮抓取流程




