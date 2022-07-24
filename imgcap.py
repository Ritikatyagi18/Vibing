import json
from turtle import shape
from flask import Flask,render_template, request,redirect,url_for,session
import cv2, numpy as np
from PIL import Image
from urllib.request import urlopen
from keras.models import load_model
import pandas as pd
import random
import spotipy as SP
import time

app=Flask(__name__)
app.secret_key = "super secret key"

#Route for homepage 
@app.route('/')
def welcome():
    return render_template('page1.html')

#Route to predict the emotion of the user
@app.route('/mood',methods=['POST'])
def checkMood():
    
    output=request.get_json()             #To receive json file sent by javascript
    result=json.loads(output)             #To convert json file back into python
    
    #Harr Cascade
    url=result['image_data_url']           #Retrieving the value of url generated from dictionary
    img = Image.open(urlopen(url))         #Retrieving image from the given url
    image = np.asarray(img)                #Converting the image into a multi dimensional array
    crop_img=img
    
    #Using haarcascade front face xml to detect the face in the image clicked
    face_cascade = cv2.CascadeClassifier('haarcascades\haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(image, 1.3, 5)
    for (x, y, w, h) in faces:
        if len(faces) == 1: #Check if one face is detected, or multiple (measurement error unless multiple persons on image)
            crop_img = img.crop((x,y,x+w,y+h))
        else:
            print("multiple faces detected, passing over image")
    def get_label(argument):
        labels = {0:'Angry', 1:'Disgust', 2:'Fear', 3:'Happy', 4:'Sad', 5:'Surprise', 6:'Neutral' }
        return(labels.get(argument, "Invalid emotion"))
    
    test_image = crop_img.resize((48,48)) #Resizing the image
    test_image = np.array(test_image)                       #Converting image into multi dimensional array
    gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)       #Converting image from BGR to RGB
    gray = gray/255
    gray = gray.reshape(-1, 48, 48, 1)
    
    #Mood Detection - Model
    testmodel=load_model('model_seq.h5') #loading our trained ML Model for mood detection
    res = testmodel.predict(gray)      #predicting   
    
    #argmax returns index of max value
    result_num = np.argmax(res)
    print("Probabilities are " + str(res[0])+"\n")
    # print("Emotion is "+get_label(result_num))
    emotion = get_label(result_num)
    print("Emotion is : ",emotion)
    # emotions = 'Happy'
    session['emotion']=emotion
    print("Session emotion : ",session['emotion'])
    #Redirecting user to another page
    return redirect(url_for('selectArtist'))

#For user to select the artist
@app.route('/selectArtist',methods=['POST','GET'])
def selectArtist():
    return render_template('page2.html')

#For music recommendation 
@app.route('/songs',methods=['POST','GET'])
def sendSongs():
    time.sleep(5)
    emotion= session.get('emotion',None)
    print("Send song : ",emotion)
    a=[]
    if(request.method=='POST'):
        ot=request.json             #To receive json file sent by javascript
        print(ot)
        at=json.loads(ot)             #To convert json file back into python object 
        singers = at['s']
        a = singers.split(',')
        print(a)
    #Authenticating spotify developer 
    client_id = '146f096c156140d8831fdb867d345a1f'
    client_secret = '31cf0698d59c4d969b1b0269bb89c982'
    redirect_uri = 'https://bhargavibhatia215.github.io/Vibing/'

    #Defining the type of data we need access for creating a playlist from spotify api
    scope = 'playlist-modify-public'
    username = 'Vibing Project'
    # emotion = at['emotion']
    # emotion = 'Happy'
    
    #Developer's token is being generated
    token = SP.util.prompt_for_user_token(username,scope,client_id,client_secret,redirect_uri)
    if token :
        def authenticate_spotify():
            print('connecting to spotify')
            sp = SP.Spotify(auth = token)   #Authenticating to spotify using token generated
            return sp
    
    #Retrieving the playlist url of the selected artist(by user)
    def selected_artists():
        df = pd.read_csv("Playlists.csv")
        playlist_url = []
        for artist in a:
            if artist != 'submit':
                for val in df.index:
                    if artist == df['Artist'][val]:
                        playlist_url.append(df['Playlist_ID'][val])
        return playlist_url
    
    #Retrieving the tracks from the playlist of artist already created by Spotify
    def get_track_uri(spotify,playlist_url):
        uris = []
        for x in playlist_url:
            str1 = spotify.playlist_tracks(x)
            val = str1['items']
            tracks_data = []
            for item in val:
                tracks_data = item['track']
                uris.append(tracks_data['uri'])
        return uris
    
    def select_mood_range():
        val = 0
        if emotion == 'Sad':
            val =  round(random.uniform(0,0.09), 2)
        elif emotion == 'Angry':
            val = round(random.uniform(0.10,0.24), 2)
        elif emotion == 'Disgust' or emotion == 'Fear':
            val = round(random.uniform(0.25,0.49), 2)
        elif emotion == 'Neutral' or emotion == None:
            val = round(random.uniform(0.50,0.74), 2)
        elif emotion == 'Surprised':
            val = round(random.uniform(0.75,0.89), 2)
        elif emotion == 'Happy':
            val = round(random.uniform(0.90,1.00), 2)
        return val
          
    #Random shuffling of the tracks, selection is done on the basis of emotion detected
    def select_tracks(spotify,top_tracks_uri,mood):
        print("selecting tracks")
        print(mood)
        random.shuffle(top_tracks_uri)
        # print(top_tracks_uri)
        selected_tracks_uri = []
        for tracks in list(top_tracks_uri):
            tracks_all_data = spotify.audio_features(tracks)
            # print(tracks_all_data)
            for track_data in tracks_all_data:
                try:
                    if mood < 0.10:
                        if(0 <= track_data['valence'] <= (mood+0.15)):
                            selected_tracks_uri.append(track_data['uri'])
                    elif 0.10 <= mood < 0.25:
                        if((mood-0.075) <= track_data['valence'] <= (mood+0.075)):
                            selected_tracks_uri.append(track_data['uri'])
                    elif 0.25 <= mood < 0.50:
                        if((mood-0.05) <= track_data['valence'] <= (mood+0.05)):
                            selected_tracks_uri.append(track_data['uri'])
                    elif 0.50 <= mood < 0.75:
                        if((mood-0.075) <= track_data['valence'] <= (mood+0.075)):
                            selected_tracks_uri.append(track_data['uri'])
                    elif 0.75 <= mood < 0.90:
                        if((mood-0.075) <= track_data['valence'] <= (mood+0.075)):
                            selected_tracks_uri.append(track_data['uri'])
                    elif mood >= 0.90:
                        if((mood-0.15) <= track_data['valence'] <= 1):  
                            selected_tracks_uri.append(track_data['uri'])
                except TypeError as te:
                    continue
        print(selected_tracks_uri)
        return selected_tracks_uri

    
    
    #Creating public playlist of 30 songs from the selected tracks
    def create_playlist(spotify, selected_tracks_uri):
        print("...creating playlist")
        user_all_data = spotify.current_user()
        user_id = user_all_data["id"]
        name = "Vibing"+ str(random.randint(0,3000)) 
        playlist_all_data = spotify.user_playlist_create(user_id, name)
        playlist_id = playlist_all_data['id']
        tracks_uris = selected_tracks_uri[0:30]
        spotify.user_playlist_add_tracks(user_id,playlist_id,tracks_uris)
        print('https://open.spotify.com/playlist/',playlist_id,sep='')
        # playlist_url = "https://open.spotify.com/embed/playlist/"+playlist_id+"?utm_source=generator"
        return playlist_id
    
    sp = authenticate_spotify()
    playlist_url = selected_artists()
    uris = get_track_uri(sp,playlist_url)
    val = select_mood_range()
    selected_tracks_uri = select_tracks(sp,uris,val)
    print(selected_tracks_uri)
    # while len(selected_tracks_uri) < 20:
    #     val = select_mood_range()
    #     #print(val)
    #     selected_tracks_uri = select_tracks(sp,uris,val)    
    playlist_id=create_playlist(sp, selected_tracks_uri)
    session['play'] = playlist_id
    return redirect(url_for('playlistDisplay'))
@app.route('/playlistDisplay')
def playlistDisplay():
    play = session.get('play',None)
    return render_template('page3.html',playlist_id = play)

if __name__=='__main__':
    app.run(debug=True)
