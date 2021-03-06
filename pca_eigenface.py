
# coding: utf-8

# In[15]:

get_ipython().magic(u'matplotlib inline')

import numpy as np
import scipy.io as sio
import scipy
import scipy.spatial
from scipy.linalg import norm
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy.linalg as linal
from sklearn.preprocessing import StandardScaler
from numpy import *

mat_contents = sio.loadmat('./umist_cropped.mat')
facedat = mat_contents['facedat']

people = facedat[0]
people1 = facedat[0][0]  #(112,92,38)
people2 = facedat[0][1]
people1_face1 = facedat[0][0][:,:,0]
people1_face15 = facedat[0][0][:,:,14]
people2_face2 = facedat[0][1][:,:,1]
people2_face15 = facedat[0][1][:,:,14]

vec_people1_face1 = people1_face1.flatten()
vec_people2_face2 = people2_face2.flatten()
pixels=112*92


# In[9]:

def mean_face(faces):
    face_mean  = np.zeros((faces.shape[0],faces.shape[1]))
    for face_num in range(faces.shape[2]):
        face_mean = face_mean + faces[:,:,face_num]
    return face_mean

def mat2vecs(mat_person):
    people_pic_size = mat_person[:][91][1].size
    # print people_pic_size
    mat_people = np.zeros((people_pic_size,pixels))
    for i in range(0,people_pic_size):
        mat_people[i]= mat_person[:,:,i].flatten()# mat_people1 是描述 class的大矩阵
    return mat_people

def ReconginitionVector(selecthr = 0.8):
    # step1: load the face image data ,get the matrix consists of all image
    FaceMat = people_set.T
    # step2: average the FaceMat
    avgImg = np.mean(FaceMat,1)
    # step3: calculate the difference of avgimg and all image data(FaceMat)
    diffTrain = FaceMat-avgImg
    #step4: calculate eigenvector of covariance matrix (because covariance matrix will cause memory error)
    eigvals,eigVects = linal.eig(mat(diffTrain.T*diffTrain))
    eigSortIndex = argsort(-eigvals)
    for i in xrange(shape(FaceMat)[1]):
        if (eigvals[eigSortIndex[:i]]/eigvals.sum()).sum() >= selecthr:
            eigSortIndex = eigSortIndex[:i]
            break
    covVects = diffTrain * eigVects[:,eigSortIndex] # covVects is the eigenvector of covariance matrix
    # avgImg 是均值图像，covVects是协方差矩阵的特征向量，diffTrain是偏差矩阵
    return avgImg,covVects,diffTrain

def judgeFace(judgeImg,FaceVector,avgImg,diffTrain):
    diff = judgeImg.T - avgImg
    weiVec = FaceVector.T* diff
    res = 0
    resVal = inf
    # 设置阈值thr1 和 thr2
    thr1 = 2.0e+30
    thr2 = 2.0e+11
    d1 = scipy.spatial.distance.euclidean(judgeImg.T,FaceVector*weiVec + avgImg)
    # res >=0 : in dataset, -1: not in dataset, -2 : not even a face 
#     if d1 >= thr2:
#         res = -2
#     elif d1 >= thr1:
#         res = -1
    if res == 0 :
        for i in range(40):
            TrainVec = FaceVector.T*diffTrain[:,i]
            if  (array(weiVec-TrainVec)**2).sum() < resVal:
                res =  i
                resVal = (array(weiVec-TrainVec)**2).sum()
    return res


# In[10]:

people_set = mat(zeros((people.size * 2,pixels)))
for i in range(people.size):
    people_set[2*i,:] = mat(people[i][:,:,8]).flatten()
    people_set[2*i + 1,:] = mat(people[i][:,:,18]).flatten()
avgImg,FaceVector,diffTrain = ReconginitionVector(selecthr = 0.9)
# print judgeFace(mat(people1_face15).flatten(),FaceVector,avgImg,diffTrain)
# print judgeFace(mat(people2_face15).flatten(),FaceVector,avgImg,diffTrain)
# 输出识别每个人时的准确率
count_total = 0.0
pic_num_total = 0
for people_num in range(people.size):
    count = 0.0
    pic_num = people[people_num].shape[2]
    for i in range(pic_num):
        judgeImg = people[people_num][:,:,i]
        judgeNum = judgeFace(mat(judgeImg).flatten(),FaceVector,avgImg,diffTrain)
        if judgeNum in ( people_num*2 , people_num*2+1 ) :
            count += 1
            count_total += 1
    pic_num_total += pic_num
    print "%d  \ttotal:%d  \taccuracy: %f %%" % (people_num,pic_num, count / pic_num * 100)
print "total accuracy: %f" % (count_total / pic_num_total)
