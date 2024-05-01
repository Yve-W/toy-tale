import numpy as np
import cv2
import os
import time
import math

def detect():
    yolo_dir = "model"  # or "tiny_yolov4" depending on which version you download
    weightsPath = os.path.join(yolo_dir, 'yolov7-tiny.weights')  # or 'yolov4-tiny.weights'
    configPath = os.path.join(yolo_dir, 'yolov7-tiny.cfg')  # or 'yolov4-tiny.cfg'
    labelsPath = os.path.join(yolo_dir, 'coco.names')  # label
    imgPath = os.path.join(yolo_dir, 'person.jpg')  # image for test
    CONFIDENCE = 0.7  # 过滤弱检测的最小概率
    THRESHOLD = 0.4  # 非最大值抑制阈值

    with open(labelsPath, 'rt') as f:
        labels = f.read().rstrip('\n').split('\n')
    # 加载网络、配置权重
    # Load the network, configure the weights
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)  

    cap = cv2.VideoCapture(0)
    
    cap.set(3,640)#摄像头采集图像的宽度320
    cap.set(4,480)#摄像头采集图像的高度240
    cap.set(5,30) #摄像头采集图像的帧率fps为30

    #View the parameters of the captured image
    print(cap.get(3))
    print(cap.get(4))
    print(cap.get(5))

    while True:
        # read the image
        ret, img = cap.read()
        if not ret:
            break

        # load the image, convert it to blob format, send it to the network input layer, get the information of the network output layer (the name of all output layers), set and forward propagation
        start = time.time()
        #img = cv2.imread(frame)
        img  = cv2.flip(img, 1)
        (H, W) = img.shape[:2]
        blobImg = cv2.dnn.blobFromImage(img, 1.0/255.0, (416, 416), None, True, False)  ## net需要的输入是blob格式的，用blobFromImage这个函数来转格式
        net.setInput(blobImg)  ## 调用setInput函数将图片送入输入层
        outInfo = net.getUnconnectedOutLayersNames()  ## 前面的yolov3架构也讲了，yolo在每个scale都有输出，outInfo是每个scale的名字信息，供net.forward使用
        layerOutputs = net.forward(outInfo)  # 得到各个输出层的、各个检测框等信息，是二维结构。
        boxes = [] # 所有边界框（各层结果放一起）
        confidences = [] # 所有置信度
        classIDs = [] # 所有分类ID
        for out in layerOutputs:  # 各个输出层
            for detection in out:  # 各个框框
                # 拿到置信度
                scores = detection[5:]  # 各个类别的置信度
                classID = np.argmax(scores)  # 最高置信度的id即为分类id
                confidence = scores[classID]  # 拿到置信度
                # 根据置信度筛查
                if confidence > CONFIDENCE:
                    box = detection[0:4] * np.array([W, H, W, H])  # 将边界框放会图片尺寸
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
        #应用非最大值抑制(non-maxima suppression，nms)进一步筛掉
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE, THRESHOLD) # boxes中，保留的box的索引index存入idxs
        # 应用检测结果
        np.random.seed(42)
        center_x = 320
        center_y = 240
        temp = 10000000
        COLORS = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")  # 框框显示颜色，每一类有不同的颜色，每种颜色都是由RGB三个值组成的，所以size为(len(labels), 3)
        if len(idxs) > 0:
            for i in idxs.flatten(): # indxs是二维的，第0维是输出层，所以这里把它展平成1维
                if labels[classIDs[i]] != 'person':
                    (x, y) = (boxes[i][0], boxes[i][1])
                    (w, h) = (boxes[i][2], boxes[i][3])
                    color = [int(c) for c in COLORS[classIDs[i]]]
                    center_x_img = x + w / 2
                    center_y_img = y + h / 2 
                    distance_to_center = math.sqrt((center_y-center_y_img)**2 + (center_x-center_x_img)**2)
                    if distance_to_center <= 150:

                    # if temp > distance_to_center:
                    #     temp = distance_to_center
                    #     index = i
                        # print (labels[classIDs[i]])
                        return labels[classIDs[i]]
                    cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)  # 线条粗细为2px
                        
                    #text = "{}: {:.4f}".format(labels[classIDs[i]], confidences[i])
        end = time.time()
        # print("YOLO1 took {:.6f} seconds".format(end - start))
        cv2.namedWindow('target detect result1',0)
        cv2.imshow('target detect result1', img)
        cv2.resizeWindow("target detect result1",1280,960)
        cv2.moveWindow("target detect result1",0,0)
        
        if cv2.waitKey(1)&0xff==ord('q'): #按Q键退出，可以改成任意键
            break
    cap.release()
    cv2.destroyAllWindows()
    return
    
    




if __name__ == '__main__':
    result = object_detection()
    print (result)


