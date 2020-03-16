import io
import os
import cv2
import moviepy
import crepe
import numpy
import csv
import srt

from time import sleep
from google.cloud import translate_v2, speech_v1, texttospeech
from moviepy.editor import *


#This function centers the text vertically in the terminal
def enters(n):
    row= os.get_terminal_size().lines
    enter= (row-n)/2
    for i in range(int(enter)):
        print()

#This function prints out the text centered horizontally and at the specified speed
def prints(str, n, input_size=0):
    col= os.get_terminal_size().columns
    length_sen= len(str)
    space= (col-length_sen)/2-input_size

    for i in range(int(space)):
        print(" ", end='', flush=True)
        
    for i in str:
        sleep(n)
        print(i, end='', flush=True)


class VideoTranslator:

    def __init__(self):

        #BEGIN TRANSLATION SETUP
        self.translate_client = translate_v2.Client()
        #END TRANSLATION SETUP

        #BEGIN GENERAL SETUP
        self.languages = {}
        for lng in self.translate_client.get_languages():
            self.languages[lng['name'].lower()] = lng['language']
        #END GENERAL SETUP

        #BEGIN AUDIO-TEXT SETUP
        self.audio_text_client = speech_v1.SpeechClient()
        self.audio_channel_count = 2
        self.enable_separate_recognition_per_channel = True
        #END AUDIO-TEXT SETUP

        #START TEXT-AUDIO SETUP
        self.text_audio_client = texttospeech.TextToSpeechClient()
        #END TEXT-AUDIO SETUP

    def translate(self, text, lng="english"):
        translation = self.translate_client.translate(text,
            target_language=self.languages[lng.lower()])
        return self.edit_transcript(translation['translatedText'])

    def get_text(self, transcript):
        return transcript[0] 
        
    def get_audio(self, local_file_path):
        with io.open(local_file_path, "rb") as f:
            content = f.read()
        return content


    def translate_video(self, url, native_lng, lng="english"):
        #video, audio = self.retrieve_video_and_audio(url)
        audio = {"content": self.get_audio(url)}
        
        full_transcript = self.split_transcript(self.get_transcript(audio, native_lng))

        with open("transcript.txt", "w") as out:
            out.write(full_transcript[0]) #fix this because it shouldnt just be a one item list

        owo = input("edit transcript xd")


        uwu = open("transcript.txt", "r")
        full_transcript = [uwu.read()]

        translated_transcript = []
        for line in full_transcript:
            translated_transcript.append(self.translate(line, lng))

        # print(translated_transcript)

        translated_audio = None 
        for i in range(len(full_transcript)):
            native_line = full_transcript[i]
            translated_line = translated_transcript[i]
            #speed_factor = 4
            if not translated_audio:
                translated_audio = self.text_to_audio(translated_line, lng, speed_factor=1)
            else:
                translated_audio = translated_audio + self.text_to_audio(translated_line, lng, speed_factor=1)


        with open("cache.mp3", "wb") as out:
            out.write(translated_audio)

        cache_audio = AudioFileClip("cache.mp3")
        new_duration = cache_audio.duration
        old_duration = videoclip.duration
        factor = new_duration/old_duration
        if factor > 4:
            factor = 4
        if factor < 0.25:
            factor = 0.25


        translated_audio2 = None
        for i in range(len(full_transcript)):
            native_line = full_transcript[i]
            translated_line = translated_transcript[i]
            speed_factor = factor
            if not translated_audio2:
                translated_audio2 = self.text_to_audio(translated_line, lng, speed_factor=factor)
            else:
                translated_audio2 = translated_audio2 + self.text_to_audio(translated_line, lng, speed_factor=factor)

        os.system("clear")

        display_text= self.get_text(full_transcript)
        display_text= "This is a transcript of the input video file in the language " + s1.upper() + " provided by the user. \n \n" + display_text+ "\n \n \n"


        display_text2= self.get_text(translated_transcript)
        display_text2= "This is a copy of the transcript in the language " +s2.upper()+ " auto-generated by google cloud api. \n \n" + display_text2

        display_text= display_text+ display_text2

        with open("transcriptfinal.txt", "w") as out:
            out.write(display_text)

        with open("output.mp3", "wb") as out:
            out.write(translated_audio2)

        audio_background = AudioFileClip("output.mp3")

        final_audio = CompositeAudioClip([audio_background])
        final_clip = videoclip.set_audio(audio_background)
        final_clip.write_videofile("result.mp4")

        os.system("clear")

        clip_resized = final_clip.fx(vfx.resize, newsize=(h, w))

        os.system("clear")

        clip_resized.write_videofile("result.mp4")

        os.system("clear")

    def edit_transcript(self, transcript):
        return transcript.replace("&#39;", "'")

    def split_transcript(self, transcript):
        return [transcript]

    def get_transcript(self, audio, native_lng):
        config = {
            "audio_channel_count": self.audio_channel_count,
            "enable_separate_recognition_per_channel": self.enable_separate_recognition_per_channel,
            "language_code": self.languages[native_lng],
        }
        response = self.audio_text_client.recognize(config, audio)
        for result in response.results:
            alternative = result.alternatives[0]

        return format(alternative.transcript)

    def get_speed_factor(self, native_line, translated_line): # incomplete
        return len(translated_line)/len(native_line)

    def determine_gender(self, frequency):
        return frequency > 170 and "female" or "male"

    def text_to_audio(self, text, lng, speed_factor, gender=None): 
        
        gender = self.determine_gender(frequency)

        if gender == "female":
            ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE
        elif gender == "male":
            ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE
        else:
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL

        # print(speed_factor)
        synthesis_input = texttospeech.types.SynthesisInput(text=text)
        voice = texttospeech.types.VoiceSelectionParams(language_code=self.languages[lng], ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE) #MALE DEFAULT FOR NOW
        audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3, speaking_rate=speed_factor, pitch=frequency/100)
        response = self.text_audio_client.synthesize_speech(synthesis_input, voice, audio_config)
        return response.audio_content


os.system("clear")

# Takes in the name of the input file, which is a .mov file
enters(1)
prints("Specify Filename: ", 0.01, 10)
s= input()

# Getting the dimensions of the original video
vid = cv2.VideoCapture(s)
h = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
w = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

# Making an audiofile out of the the video file, named "trying.wav"
videoclip = VideoFileClip(s)
audioclip = videoclip.audio
audioclip.write_audiofile("trying.wav", verbose=False)
os.system("clear")

# taking inputs of native language and changin language
enters(1)
prints("Input Language: ", 0.01, 8)
s1 = str(input()).strip()

print()
print()

prints("Output Language: ", 0.01, 8)
s2 = str(input()).strip()

#finsing average frequency of the input audio
lst = list()
os.system("clear")
os.system("crepe trying.wav --step-size 100")

with open ('trying.f0.csv',newline='') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for row in data:
        lst.append(row[1])

lst = lst[1:]
lst = [float(s) for s in lst]
lst.sort()
length = len(lst)

DELTA = 0.1
lst = lst[int(length*DELTA):-int(length*DELTA)]
frequency = sum(lst) / len(lst)

os.system("clear")

""" Ideas: Randomized language """

vt = VideoTranslator()
os.system("clear")
vt.translate_video("trying.wav", s1, s2)
os.system("clear")
os.remove("trying.wav")
os.remove("cache.mp3")
os.remove("output.mp3")
os.remove("trying.f0.csv")
os.system("clear")

enters(1)
prints("Task completed. Please check directory for new video.", 0.02)
for _ in range(5):
    print()