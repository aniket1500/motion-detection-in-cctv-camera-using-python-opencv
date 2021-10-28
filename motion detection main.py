import requests,csv,os,cv2,time
import pandas as pd
import datetime as dt
 
vidRec = False
first_frame = None
status_list = [None, None]
times = []
df = pd.DataFrame(columns=["Start", "End"])

video = cv2.VideoCapture(1)
# videocapture(0) is for laptop's integrated camera
# videocapture(1) is for external camera connected

frame_width = int(video.get(3))
frame_height = int(video.get(4))

size = (frame_width, frame_height)
APP_FOLDER = 'F:\Desktop\ML Project\logs'
totalFiles = 0
totalDir = 0
# to count the number of previously recorded files in the folder
# so that this recording is saved as a new file
for base, dirs, files in os.walk(APP_FOLDER):
    print('Searching in : ',base)
    for directories in dirs:
        totalDir += 1
    for Files in files:
        totalFiles += 1


result = cv2.VideoWriter('logs/Record '+str(totalDir + totalFiles+1)+'.avi', cv2.VideoWriter_fourcc(*'MJPG'), 10, size)
sendNoti = False
while True:
    check, frame = video.read()
    status = 0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if first_frame is None:
        first_frame = gray
        # cv2.imwrite('first_frame.png', first_frame)
        continue    

    delta_frame = cv2.absdiff(first_frame, gray)
    thresh_delta = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_delta = cv2.dilate(thresh_delta, None, iterations=0)
    major = cv2.__version__.split('.')[0]
    if major == '3':
        ret, contours, hierarchy = cv2.findContours(
            thresh_delta.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(
            thresh_delta.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # to ignore noise from frame
    for contour in contours:
        if cv2.contourArea(contour) < 10000:
            continue
        status = 1
        # to create a rectangle around the object
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

    status_list.append(status)
    status_list = status_list[-2:]

    if status_list[-1] == 1 and status_list[-2] == 0:
        times.append(dt.datetime.now())
        vidRec = True
    if vidRec:
        result.write(frame)
        sendNoti = True
        
    if status_list[-1] == 0 and status_list[-2] == 1:
        times.append(dt.datetime.now())
        # cv2.imwrite('output_frame.png', frame)
        vidRec = False

    # cv2.imshow("Capturing", gray)
    # cv2.imshow("delta", delta_frame)
    
    cv2.imshow("thresh", thresh_delta)
    cv2.imshow("frame", frame)
    
    key = cv2.waitKey(1)
    if key == ord("q"):
        break


filename = "time_record.csv"
rows = ['year', 'month', 'day', 'hours', 'minutes', 'seconds', 'milliseconds']
rows3 = []
rows2 = []

#to send notifications
if sendNoti:
    message = 'Hello User, Some activity is detected by the CCTV camera in your area, Please check the logs for further information'
    base_url = 'https://api.telegram.org/bot1716173591:AAE-RsJvY6JN96btv-MQd9AxLjne0UCPKLU/sendMessage?chat_id=-483333294&text={}'.format(
        message)
    requests.get(base_url)

for i in times:
    rows2.append(i.strftime('%Y'))
    rows2.append(i.strftime('%B'))
    rows2.append(i.strftime("%d"))
    rows2.append(i.strftime('%H'))
    rows2.append(i.strftime('%M'))
    rows2.append(i.strftime('%S'))
    rows2.append(i.strftime('%f'))
    rows3.append(rows2)
    rows2 = []

# writing time stamps to the sheet
with open(filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(rows)
    csvwriter.writerows(rows3)
video.release()

cv2.destroyAllWindows
