import cv2
import numpy as np
import mediapipe as mp
import random

# Swap two frames in the image
def swap():
    global stack,shl
    if len(stack)==2:
        shl[stack[0]],shl[stack[1]]=shl[stack[1]],shl[stack[0]]
        stack=[]

# Identify spatial location and swap frames
def spacial_location_check(cx,cy):
    global x
    chk=-1
    for i in range(3):
        for j in range(3):
            chk+=1
            if cx in range(bxs[j,i,0],bxl[j,i,0]) and cy in range(bxs[j,i,1],bxl[j,i,1]):
                x.append([i,j])
                if x[0]!=x[-1]:
                    x=[]
                elif len(x)==25:
                    stack.append(chk)
                    if len(stack)>1:
                        swap()
                    x=[]

if __name__ == '__main__':
    bxs=np.full((3,3,2),0)
    bxl=np.full((3,3,2),0)
    si=600
    bl=[0,si//3,(si//3)*2,si]
    for i in range(3):
        for j in range(3):
            bxs[i,j]=(bl[i],bl[j])
            bxl[i,j]=(bl[i+1],bl[j+1])
    
    # Load Puzzle image, split image into pieces and randomly shuffle the frames
    imgx = cv2.imread(r'img_5terre.jpg')
    imgx = cv2.resize(imgx,(si,si), fx = 0.1, fy = 0.1)
    stack,x,shl=[],[],[]
    for i in range(3):
            for j in range(3):
                shl.append(imgx[bl[i]:bl[i+1],bl[j]:bl[j+1]])
    random.shuffle(shl)

    # Capture live video
    cap = cv2.VideoCapture(0)
    
    # initialize the Hands class and store it in a variable
    mp_hands = mp.solutions.hands
    
    # Set hands function which will hold the landmarks points
    hands = mp_hands.Hands(static_image_mode=True)
    
    # Drawing function of hand landmarks on the image
    mp_drawing = mp.solutions.drawing_utils

    while True:
        # Capture and process image frame from video
        success, image = cap.read()
        image=cv2.flip(image,1)
        image = cv2.resize(image,(si+200,si), fx = 0.1, fy = 0.1)
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(imageRGB)
        ck=0
        for i in range(3):
            for j in range(3):
                if ck in stack:
                    image[bl[i]:bl[i+1],bl[j]:bl[j+1]]=cv2.blur(shl[ck],ksize=(15,15))
                else:
                    image[bl[i]:bl[i+1],bl[j]:bl[j+1]]=shl[ck]
                ck+=1
                
        # Locate spatial location of finger and mark image frame piece and swap pieces
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks: 
                for id, lm in enumerate(handLms.landmark):
                    if id == 8 :
                        h, w, c = image.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        spacial_location_check(cx,cy)
                        cv2.circle(image, (cx, cy), 25, (255, 0, 0), cv2.FILLED)
                mp_drawing.draw_landmarks(image, handLms, mp_hands.HAND_CONNECTIONS)
        cv2.imshow("output", image)
        if (cv2.waitKey(1) & 0xFF == ord('q')):
                break
    cv2.destroyAllWindows()
    cap.release()
