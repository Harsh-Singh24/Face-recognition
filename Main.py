from tkinter import *
from tkinter import ttk
from tkinter import filedialog
#from tkinter import * here we do not need to use * we can directly use win = Tk()
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
import cv2
import os
from datetime import datetime
import time
import threading
import face_recognition
import pygame
from playsound import playsound
import pickle




#Module 1: functions
state = 'logoff'
path = ''
images = []
classNames = []
read_data = pd.DataFrame()
Student_Data = pd.DataFrame()
file_path = ''
df = pd.DataFrame()
encodeList = []

def toggle_frame_steps(state_value):
    global state
    
    for widget in frame_steps.winfo_children():
        # Check if the widget has a 'state' attribute (buttons, entries, etc.)
        if isinstance(widget, (Button, Entry, Checkbutton, Text)):
            widget.config(state='disabled' if state_value == 'logoff' else 'normal')

def login():
    global state  # Declare 'state' as global so it can be modified
    
    if state == 'login':
        label_login.config(text='Already logged in')
    
    else:
        name = entry_name.get()  # Get input from entry_name
        password = entry_password.get()  # Get input from entry_password
    
        if name == 'admin001' and password == 'HarshGMS':
            label_login.config(text=f'Logged in as {name}')
            state = 'login'  # Update the global variable 'state'
            print(state)
            entry_name.delete(0, 'end')
            entry_password.delete(0, 'end') 
            toggle_frame_steps(state)
            return state
        
        else:
            label_login.config(text='Invalid credentials')  # Handle wrong credentials
        
    entry_name.delete(0, 'end')
    entry_password.delete(0, 'end') 
    
      
def logout():
    global state
    
    if state == 'logoff':
        label_login.config(text='Already logged-out')
    else:    
        state = 'logoff'
        print(state)
        label_login.config(text='Succefully logout')
        toggle_frame_steps(state)

def select_file():
    # Open a file dialog to select a CSV or Excel file
    global file_path
    
    file_path = filedialog.askopenfilename(
        title="Select a CSV or Excel file",
        #filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xls *.xlsx")]
        filetypes=[("CSV Files", "*.csv")]
    )
    print(file_path)
    
    
    
    if file_path:  # If a file is selected
        label_logs.config(text=f"Selected File: {file_path}")
       
    
def select_folder():
    global path
    
    path = filedialog.askdirectory()  # Opens the folder selection dialog
    if path:
        label_logs.config(text=f"Selected Folder: {path}")  # Update label with the folder path
        
def load():
    global images
    global classNames
    global read_data
    global path
    
    print(path)
    allImages = os.listdir(path)
    print(allImages)
    try:
        for cl in allImages:
            currentImage = cv2.imread(f'{path}/{cl}')
            images.append(currentImage)
            classNames.append(os.path.splitext(cl)[0])
            
            print(images)
        print(classNames)
        st = len(classNames)
        
        
        #pickling code goes there
        try:
            file_image_pickle = 'image_pickle.pkl'
            fileobj_image_pickle = open(file_image_pickle,'wb')
            pickle.dump(images,fileobj_image_pickle)
            fileobj_image_pickle.close()
            print(f'Total {st} images read successfully!')
            read_data = pd.DataFrame(classNames,columns=['Admission No.'])
            print(read_data)
            label_logs.config(text="Folder succefully loaded")              
        except Exception as e:
            error = str(e)
            label_logs.config("error in saving pickle file")
                     
    except Exception as e:
        error = str(e)
        label_logs.config(text=f"error : {error}")
        
def load_file():
    global read_data
    global Student_Data
    global file_path
    global df
    try:
        print(file_path)
        Student_Data = pd.read_csv(file_path,header=0)
        Student_Data['Admission No.'] = Student_Data['Admission No.'].str.replace('/','_')
        df = pd.merge(read_data,Student_Data,on='Admission No.',how='left')
        print(Student_Data.shape)
        print(df.shape)
        
        #Pickling code goes here
        file_dataframe_pickle = 'dataframe.pkl'
        fileobj_dataframe_pickle = open(file_dataframe_pickle,'wb')
        pickle.dump(df,fileobj_dataframe_pickle)
        fileobj_dataframe_pickle.close()
        
        label_logs.config(text="File succefully loaded")
        
    except Exception as e:
        error = str(e)
        label_logs.config(text=f"error : {error}") 
        
        

def FindEncoding():
    global images
    global encodeList
    total_images = len(images)
    
    #image unpickling
    file1 = 'image_pickle.pkl'
    fileobj1 = open(file1,'rb')
    images = pickle.load(fileobj1)
    total_images = len(images)
    
    try:
        for idx, img in enumerate(images):
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
            # Update the progress bar
            progress_bar['value'] = (idx + 1) / total_images * 100
            win.update_idletasks()  # Force GUI to update progress
        print(encodeList)
        label_logs.config(text="Training successful")
        
        #pickle code goes ther
        file_encode_pickle = 'encode_pickle.pkl'
        fileobj_encpde_pickle = open(file_encode_pickle,'wb')
        pickle.dump(encodeList,fileobj_encpde_pickle)
        fileobj_encpde_pickle.close()
        
    except Exception as e:
        print(e)
        label_logs.config(text="Error in Training")

# Function to run FindEncoding() in a separate thread
def run_training():
    thread = threading.Thread(target=FindEncoding)
    thread.start()        


def markAttendance(name):
    # Check if the file 'Attendance.csv' exists in the current directory
    if not os.path.exists('Attendance.csv'):
        # Create the file if it doesn't exist and write the header (if needed)
        with open('Attendance.csv', 'w') as f:
            f.writelines('Name,DateTime')  # Writing header row
    
    # Open the file in append and read mode ('r+')
    with open('Attendance.csv', 'r+') as f:
        mydb = f.readlines()
        nameList = []
        for line in mydb:
            entry = line.split(',')
            nameList.append(entry[0])
        
        # If the name is not in the file, add it with the current date and time
        if name not in nameList:
            nows = datetime.now()
            dtSrting = nows.strftime('%d-%m-%y:%H:%M:%S')
            f.writelines(f'\n{name},{dtSrting}')


            
image_path = 'My School.png'           
def resize_image(image_path, sys_width):
    image = Image.open(image_path)
    
    # Set the new width to 0.2701 times of sys_width
    new_width = int(0.58 * sys_width)
    
    # Maintain the aspect ratio and calculate the corresponding height
    aspect_ratio = image.height / image.width
    new_height = int(new_width * aspect_ratio)
    
    # Resize the image using LANCZOS (equivalent to the old ANTIALIAS)
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(resized_image)             
            
            
def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play(-1)
    
def stop_sound():
    pygame.mixer.music.stop()
    
    
pygame.mixer.init() 

sound_file = '2.Alert_Track.mp3'   

sound_played = False
sound_thread = None

def launch():
    global encodeList
    global sound_played
    global sound_thread
    global sys_width
    global sys_height
    global sound_file
    
    
    #encode unpickling
    file2 = 'encode_pickle.pkl'
    fileobj2 = open(file2,'rb')
    encodeList = pickle.load(fileobj2)
    print(encodeList)
    
    #df unpickling
    file3 = 'dataframe.pkl'
    fileobj3 = open(file3,'rb')
    df = pickle.load(fileobj3)
       #print(df.info(describe = 'all'))
    
    # Get system's screen width and height
    win = Tk()
    win.destroy()

    capture = cv2.VideoCapture(0)

    # Get the original dimensions of the camera feed
    original_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate the scaling factor to fit the system's screen width
    scale_factor = sys_width / original_width
    new_width = sys_width
    new_height = int(original_height * scale_factor)

    while True:
        success, img = capture.read()
        
        # Resize the image to match the system's screen width, maintaining aspect ratio
        img = cv2.resize(img, (new_width, new_height))
        
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # For face recognition, use the smaller image
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        FacesCurrentFrame = face_recognition.face_locations(imgS)
        encodesCurrentFrame = face_recognition.face_encodings(imgS, FacesCurrentFrame)

        face_detected = False

        for encodeFace, faceLocation in zip(encodesCurrentFrame, FacesCurrentFrame):
            matches = face_recognition.compare_faces(encodeList, encodeFace)
            distance = face_recognition.face_distance(encodeList, encodeFace)
            match_index = np.argmin(distance)
            
            if matches[match_index]:
                face_detected = True
                name = df['Student Name'][match_index]
                mot = df['Mode Of Transport'][match_index]
                
                if mot == 'School' and not sound_played:
                    sound_thread = threading.Thread(target=play_sound, args=(sound_file,))
                    sound_thread.start()
                    sound_played = True
                
                y1, x2, y2, x1 = faceLocation
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

                if mot == 'School':
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.rectangle(img, (x1, y2-35), (x2, y2), (255, 255, 255), cv2.FILLED)
                    
                elif mot == 'Private':
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2-35), (x2, y2), (255, 255, 255), cv2.FILLED)

                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 139), 2)
                cv2.putText(img, mot, (x1 + 6, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 139), 2)

                markAttendance(name)
        
        if not face_detected and sound_played:
            stop_sound()
            sound_played = False

        # Resize the OpenCV window to match the screen width and display the frame
        cv2.namedWindow('Webcam', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Webcam', new_width, new_height)
        cv2.imshow('Webcam', img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    capture.release()
    cv2.destroyAllWindows()
    pygame.mixer.music.stop()
    pygame.quit()            
        
#module 2: Main window customize
#main windows
win =Tk()
win.title("Harsh International School : Gate montitoring system") #for title 
win.iconbitmap('My school logo.ico') #for logo
win.config(bg = "grey64")

#Dimension and geometry
sys_width = win.winfo_screenwidth() 
print(sys_width)
sys_height = win.winfo_screenheight()
print(sys_height)

win.geometry(f'{sys_width}x{sys_height}+0+0')


#Header
lab_header = Label(win,text = 'Harsh International School',font = ("Time New Roman",25,"bold"),bg = 'red',fg='white')
lab_header.place(x=0,y=0,width=sys_width,height=(0.058 * sys_height))
print(f'coordinates of lab_header width = {sys_width} and Hieght = {0.058 * sys_height}')

#module 3: login
#Frame for login and Procedure
frame_procedure = Frame(win, bg='grey64',bd=5, relief='ridge')
frame_procedure.place(x=(0.01* sys_width),y=(0.068* sys_height),height=(0.83 * sys_height), width=(0.2409 * sys_width))
print(f'coordinates of frame x = {0.01* sys_width} , y = {(0.068* sys_height)}, width = {(0.2409 * sys_width)} and Hieght = {0.83 * sys_height}')

#login pannel
frame_login_panel = Frame(frame_procedure,bg = 'grey64', bd= 1,relief='ridge')
frame_login_panel.place(x=(0.0048 * sys_width),y=(0.0048* sys_height),height=(0.166 * sys_height), width=(0.2243 * sys_width))
frame_login_panel_height = (0.166 * sys_height)
frame_login_panel_width = (0.2243 * sys_width)
print(f'coordinates of frame x = {0.0048 * sys_width} , y = {(0.0048* sys_height)}, width = {(0.2243 * sys_width)} and Hieght = {(0.166 * sys_height)}')

label_name = Label(frame_login_panel,text = 'Name', font=('Times New Roman',20),bg="grey64")
label_name.place(x= 0,y = 0.010 * sys_height, width = (0.049 * sys_width), height = (0.0415 * sys_height))

entry_name = Entry(frame_login_panel,font=('Times New Roman',15),bg="snow",bd = 1,relief='ridge')
entry_name.place(x= (0.052 * sys_width),y = 0.010 * sys_height, width = (0.168 * sys_width), height = (0.0415 * sys_height))

label_password = Label(frame_login_panel,text = 'Password', font=('Times New Roman',20),bg="grey64")
label_password.place(x= 0,y = (0.062* sys_height), width = (0.0748 * sys_width), height = (0.0415 * sys_height))

entry_password = Entry(frame_login_panel,font=('Times New Roman',15),bg="snow",bd = 1,relief='ridge',show="*")
entry_password.place(x= (0.0778* sys_width),y = (0.062* sys_height), width = (0.1416 * sys_width), height = (0.0415 * sys_height))

button_login = Button(frame_login_panel,text = 'login',font = 20 , bd=1,relief='ridge',command=login)
button_login.place(x = (.005 * sys_width),y = (0.1141* sys_height), width = (0.0748 * sys_width), height = (0.0415 * sys_height))

label_login = Label(frame_login_panel,text = 'Please loggin', font = ('Times New Roman',10),bg = 'grey64',fg='red')
label_login.place(x = (0.0848 * sys_width),y = (0.1141* sys_height), width = (0.1380 * sys_width), height = (0.0415 * sys_height))


#module 4 : steps
frame_steps = Frame(frame_procedure,bg='grey64', bd= 1,relief='ridge')
frame_steps.place(x=(0.0048 * sys_width),y=(0.1756 * sys_height),height=((0.6496 * sys_height)-10), width=(0.2243 * sys_width))

button_logout = Button(frame_steps,text = 'log-out',font = 20 , bd=1,relief='ridge',command=logout)
button_logout.place(x = (0.07475 * sys_width),y = (0.010 * sys_height), width = (0.0748 * sys_width), height = (0.0415 * sys_height))

label_steps = Label(frame_steps,text='Steps to follow',font = ('Times New Roman',10),bg = 'grey64',fg='red')
label_steps.place(x= 0,y = (0.0565* sys_height),  width = (0.070 * sys_width), height = (0.0415 * sys_height))

#select file

label_folder = Label(frame_steps,text= '1. Select the folder of images',font=('Times New Roman',13),bg = 'grey64',)
label_folder.place(x = 0, y = 0.11 * sys_height,height=(0.01852 * sys_height))
button_select = Button(frame_steps, text="Select Folder", command=select_folder)
button_select.place(x=10, y=0.14 * sys_height,height=(0.03 * sys_height),width=((0.2243 * sys_width)/3))
button_load = Button(frame_steps, text="Load folder", command=load)
button_load.place(x=(0.1423 * sys_width), y=0.14 * sys_height,height=(0.03 * sys_height),width=((0.2243 * sys_width)/3))


label_path = Label(frame_steps,text= '2. Select the file',font=('Times New Roman',13),bg = 'grey64',)
label_path.place(x = 0, y = 0.18 * sys_height,height=(0.01852 * sys_height))
button_select_path = Button(frame_steps, text="Select File", command=select_file)
button_select_path.place(x=10, y=(0.21 * sys_height),height=(0.03 * sys_height),width=((0.2243 * sys_width)/3))
button_load_path = Button(frame_steps, text="Load file", command=load_file)
button_load_path.place(x=(0.1423 * sys_width), y=(0.21 * sys_height),height=(0.03 * sys_height),width=((0.2243 * sys_width)/3))

label_train = Label(frame_steps,text= '3. Train the model',font=('Times New Roman',13),bg = 'grey64',)
label_train.place(x = 0, y = 0.25 * sys_height,height=(0.01852 * sys_height))
button_train = Button(frame_steps, text="Train", command=FindEncoding)
button_train.place(x=10, y=(0.28 * sys_height),height=(0.03 * sys_height),width=((0.2243 * sys_width)-20))

# Progress bar
progress_bar = ttk.Progressbar(frame_steps, orient=HORIZONTAL, length=300, mode='determinate')
progress_bar.place(x=10, y=(0.35 * sys_height), height=(0.03 * sys_height), width=((0.2243 * sys_width) - 20))



#module 5 : log printer
label_logs = Label(frame_steps,text= 'Hi I will inform you about the status of your application and will also let you know if there is any error occured',font=('Times New Roman',12),bg = 'grey64',fg='red',wraplength=(0.2243 * sys_width))
label_logs.place(x= 5,y = ((0.5496 * sys_height)-10),  width = ((0.2243 * sys_width)-10), height = ((0.1 * sys_height)-5))


#module 6 : player
label_launch = Label(win,text= 'Welcome to new our Gate Monitoring System software, click on launch to open the camera.',font=('Times New Roman',12),bg = 'grey64',fg='red',wraplength=(0.4486 * sys_width))
label_launch.place(x = (0.2609 * sys_width) ,y=(0.068* sys_height))
button_launch = Button(win, text="Lauch", command=launch)
button_launch.place(x = (0.7195 * sys_width) ,y=(0.068* sys_height),height=(0.03 * sys_height),width=((0.2243 * sys_width)/3))

#module 7 : Image
resized_image = resize_image(image_path, sys_width)
label_image = Label(win, image=resized_image)
label_image.place(x=(0.34045 * sys_width),y=(0.11* sys_height))


#module 8 : disable frame
toggle_frame_steps(state)

win.mainloop() #continously run window 