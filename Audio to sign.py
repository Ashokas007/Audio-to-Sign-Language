import nltk
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords, wordnet
import speech_recognition as sr
import os
import subprocess
import time
import cv2
# nltk.download('wordnet')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('stopwords')

lemmatized_tokens = []

def get_wordnet_pos(tag):
    if tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('R'):
        return wordnet.ADV
    elif tag.startswith('J'):
        return wordnet.ADJ
    else:
        return wordnet.NOUN  # Default to noun if POS tag is not recognized

def perform_lemmatization(tokens):
    lemmatizer = WordNetLemmatizer()
    pos_tags = pos_tag(tokens)
    lemmatized_tokens = [lemmatizer.lemmatize(token, pos=get_wordnet_pos(tag)) for token, tag in pos_tags]
    return lemmatized_tokens

def process_text(text):
    global lemmatized_tokens
    # Tokenize the text
    tokens = word_tokenize(text)
    print("Tokens:", tokens)

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    stop_words.discard('a')
    stop_words.discard('y')
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    print("Filtered Tokens:", filtered_tokens)

    # Lemmatize the tokens based on POS tags
    lemmatized_tokens = perform_lemmatization(filtered_tokens)
    print("Lemmatized Tokens:", lemmatized_tokens)
    return lemmatized_tokens

def list_video_files(folder_path):
    video_extensions = ['.mp4', '.avi', '.mkv', '.flv', '.mov']
    video_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(tuple(video_extensions))]
    return video_files

def play_video(video_files,text):
    window_name = 'Multi-Video Player'

# Create a named window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    for video_file in video_files:
        cap = cv2.VideoCapture("videos\\"+video_file)
    
        # Check if video file was opened successfully
        if not cap.isOpened():
            print("Error: Could not open video file:", video_file)
            continue
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = int(1000 / (fps * 2))
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            subtitle = text
            font_scale = 1
            font_thickness = 3
            font = cv2.FONT_HERSHEY_SIMPLEX

            # Calculate the position dynamically based on the frame dimensions
            text_size = cv2.getTextSize(subtitle, font, font_scale, font_thickness)[0]
            text_x = int((frame.shape[1] - text_size[0]) / 2)
            text_y = frame.shape[0] - 50

            cv2.putText(frame, subtitle, (text_x, text_y), font, font_scale, (186 , 184, 108), font_thickness)
        
        # Display the frame
            cv2.imshow(window_name, frame)
        
        # Wait for a small delay between frames     
            if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
                break
    
    # Release the video capture object
        cap.release()

    # Close the OpenCV window
    cv2.destroyAllWindows()
def live_audio_to_text():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print("Text from live audio: ", text)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

def get_video_duration(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        cap.release()
        return duration
    except Exception as e:
        print("Error:", e)
        return 0



if __name__ == "__main__":
    text1 = live_audio_to_text()
    
    if text1:
        lemmatized_tokens = process_text(text1)

        if not lemmatized_tokens:
            print("No valid tokens obtained from the input text.")
            exit()

        folder_path = r'videos'  
        video_files = list_video_files(folder_path)
        
        matched_videos = []
        for token in lemmatized_tokens:
           if token=="say" or token=="set":
               continue
           if token=="tension" or token=="attention":
               continue
           if token=="default" or token=="record":
               token="depart"
          # Split token into letters
           letters = list(token.lower())
           print(letters)
           match_found = False
    
           # Search videos based on letters
           for video_file in video_files:
            video_name_without_extension = video_file.lower().split('.')[0]
        
            # Check if the video file matches the token directly
            if token.lower() == video_name_without_extension.lower():
                matched_videos.append(video_file)
                match_found = True
                break  # Break out of the inner loop once a match is found+
    
           # If no direct match is found, search based on letters
           if not match_found:
             for letter in letters:
                 for video_file in video_files:
                     video_name_without_extension = video_file.lower().split('.')[0]
                     if letter == video_name_without_extension.lower():
                         matched_videos.append(video_file)
            
        if matched_videos:
            print(f"Matched videos: {matched_videos}")
            play_video(matched_videos,text1)
                
                
        else:
            print("No matching videos found.")
