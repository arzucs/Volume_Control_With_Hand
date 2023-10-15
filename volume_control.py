import cv2
import time
import imutils
import math
import numpy as np
import pycaw # https://github.com/AndreMiras/pycaw , ses seviyesini ayarlamak içim gereken modül bu sayfadan alındı
import HandTrackingModule as htm # el takip modülü
from comtypes import CLSCTX_ALL
from cvzone.HandTrackingModule import HandDetector
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


cap= cv2.VideoCapture(0)

pTime=0 #önceki zaman
detector= HandDetector(detectionCon= 0.6) #güvenilirlik değeri(detectionCon) ne düşükse eli o kadar iyi bulur


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute() #seszize alma
# volume.GetMasterVolumeLevel() #ana ses seviyesi
volRange = volume.GetVolumeRange() #ses seviyesi aralığı
#volume.SetMasterVolumeLevel(-20.0, None) #ses seviye hacmini ayarlama ,ayarlamadan önce ses seviyesini görmek gerek, üstteki satır print ile yazdırılır=(-65.25, 0.0, 0.03125)
                                                #ses -20,0iken normal ses 26,ses 0.0 iken 100                       #yani aralık -65 de 0'a kadar, diğer değer göz ardı edilir
minVol = volRange[0]
maxVol = volRange[1]

vol=0
volBar=400

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1) #y eksenine göre simetrik
    img = imutils.resize(img, width=640, height=420)
    hands, img = detector.findHands(img, flipType=False) # başta y eksenine gre simetriğini aldığımız için flipType'ın False olması gerekiyo
    
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        bboxInfo = hand["bbox"]
        if len(lmList) !=0:
            #print(hands[4], hands[8])
            
            x1 , y1= lmList[4][0] , lmList[4][1] #[4, 278, -91] 4=baş parmak ,278=0.eleman, -91= 1.eleman 
            x2 , y2 =lmList[8][0] , lmList[8][1]
            cx = (x1 + x2)//2 # orta nokta bulunur
            cy = (y1 + y2)//2
            #cx , cy = (x1 + y1)//2, (y1 , y2)//2
            #length = hypot(x2 - x1, y2 - y1)
            
            #print("El Noktaları:", lmList)
            #print("Sınırlayıcı Kutu Bilgisi:", bboxInfo)

            for lm in lmList:
                
                cv2.circle(img, (x1, y1), 12, (0, 255, 0), -1) 
                cv2.circle(img, (x2, y2), 12, (0, 255, 0), -1) 
                cv2.line(img,(x1, y1),(x2, y2),(0, 255, 0), 2) # 4 ve 8 arası çizgi çizer
                cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
                
                lengt= math.hypot(x2-x1,y2-y1) # 4 ve 8 arası çizgi uzunluğu hesaplar
                #print(lengt)
                
                # hand 50 - 250
                # vol range -65 - 0
                vol = np.interp(lengt, [50,250], [minVol , maxVol]) # lengt=  [50,250] aralığında dönüştürmek istediğimiz değer, [minVol , maxVol]= dönüştürmek istediğimz aralık 
                volBar = np.interp(lengt, [ 50, 250 ], [ 400, 150 ]) # ses seviyesinin bar üzerine görmek için dönüşümü 
                #print(int(lengt),vol)
                volume.SetMasterVolumeLevel(vol, None) 
                if lengt< 45:
                    cv2.circle(img, (cx, cy), 12, (0, 0, 255), -1)
                    
        cv2.rectangle(img , (50, 150),(85, 400),(0, 215, 255), 3) 
        cv2.rectangle(img , (50, int(volBar)), (85, 400),(0, 215, 255),cv2.FILLED)

    cTime= time.time() #şimdiki zaman
    fps= 1/(cTime-pTime) 
    pTime=cTime
    
    cv2.putText( img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 0.6, (180,105,255), 2) #fps yazısının özellikleri, f'FPS: {int(fps)}' fps değerini tam sayı yazdırmak için
    cv2.imshow("frame", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()

    

    