#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 14:13:20 2022

@author: anastasialebedeva
"""

import numpy as np
import cv2 as cv
from PIL import ImageGrab
from sklearn.cluster import KMeans
from collections import Counter


def find_image_on_screen(image_path):
    '''
    Parameters
    ----------
    image_path : STR
        путь до изображения, которое ищем на экране.

    Returns
    -------
    largest_cluster_center : TUPLE
        координаты середины объекта на экране.

    '''
    img2 = ImageGrab.grab().convert('L')
    img2 = np.array(img2)
    img1 = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
    (hA, wA) = img2.shape[:2]

    # Initiate SIFT detector
    sift = cv.SIFT_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)   # or pass empty dictionary
    flann = cv.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # Need to draw only good matches, so create a mask
    points = []
    # print(len(matches))
    for match in matches:
        if match[0].distance < 0.6*match[1].distance:
            p2 = kp2[match[0].trainIdx].pt
            points.append((int(p2[0]), int(p2[1])))

    try:
        kmeans = KMeans(n_clusters=2).fit(points)
        counter = Counter(kmeans.labels_)
        largest_cluster_idx = np.argmax(counter.values())
        largest_cluster_center = kmeans.cluster_centers_[largest_cluster_idx]
        largest_cluster_center = [int(x) for x in largest_cluster_center]
        # print(largest_cluster_center)
        '''
        img3 = cv.cvtColor(img2, cv.COLOR_GRAY2BGR)
        for point in points:
            img3 = cv.circle(img3, point, radius=5,
                             color=(255, 0, 0), thickness=5)
        img3 = cv.circle(img3, largest_cluster_center,
                         radius=10, color=(0, 255, 0), thickness=10)
        im_pil = Image.fromarray(img3)
        im_pil.show()
        '''

    except ValueError:
        methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED',
                   'cv.TM_CCORR_NORMED']
        centers = []
        for meth in methods:
            img = img2.copy()
            method = eval(meth)
            result = cv.matchTemplate(img, img1, method)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            height, width = img1.shape[:2]
            top_left = max_loc
            bottom_right = (top_left[0] + width, top_left[1] + height)
            centre = ((top_left[0]+bottom_right[0])//2,
                      (top_left[1]+bottom_right[1])//2)
            centers.append(centre)
            # cv.rectangle(img, top_left, bottom_right, (255,0,0),5)
            # im_pil = Image.fromarray(img)
            # im_pil.show()
        counter = Counter(centers).most_common()
        largest_cluster_idx = max([i[1] for i in counter])
        largest_cluster_center = centers[largest_cluster_idx]
        '''
        img3 = cv.cvtColor(img2, cv.COLOR_GRAY2BGR)
        img3 = cv.circle(img3, largest_cluster_center,
                         radius=10, color=(0, 255, 0), thickness=10)
        im_pil = Image.fromarray(img3)
        im_pil.show()
        '''
    return largest_cluster_center
