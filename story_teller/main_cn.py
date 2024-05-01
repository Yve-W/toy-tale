from model_cn import BaiduAIModel
import threading
import time
import cv2
import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from recordVoice import get_audio
import object_detection
import enToCn
import serial
ser = serial.Serial('/dev/ttyACM0',9600)#change ACM number as found from ls /dev/tty/ACM*

# Example usage:
models = BaiduAIModel()
# Start the sound player threadpip
thread = threading.Thread(target=models.sound_player)
thread.daemon = True  # Daemon threads exit when the program does
thread.start()
resources_path = os.path.join(os.path.dirname(__file__), "resources")
audio_file_path = os.path.join(resources_path, "recording.wav")

while True:
    try:
        #receive pressure sensor data from arduino
        while True:
            read_serial=ser.readline()
            pressure = int (ser.readline(),16)
            time.sleep(1)
            print(pressure)
            if pressure > 200:
                break
        #start the object detection
        word = object_detection.detect()
        word = enToCn.translate_text(word)
        # word = "frog"
        print("word:", word)
        start_wav_filename=f"{word}.wav"
        story_wav_filename = f"{word}-story.wav"
        picture_wav = f"{word}-picture.wav"

        text = f"哦我知道了，你向我展示的是 {word}. 你想让我讲一个关于 {word}的故事吗 ?"
        models.generate_speech(text, start_wav_filename, cache_key=start_wav_filename,use_cache = False)
        models.play_speech(start_wav_filename, wait=True)
        get_audio(audio_file_path)
        print("Recording done.")
        try:
            transcription_text = models.transcribe_audio(audio_file_path).lower()
            print(transcription_text)
        except Exception as e:
            transcription_text = "shi-de" # models.transcribe_audio(audio_file_path).lower()
        print("Transcription:", transcription_text)
        if "tui-chu" in transcription_text or "guan-bi" in transcription_text:
            models.generate_speech("好的再见", "goodbye.wav", cache_key="goodbye.wav")
            models.play_speech('goodbye.wav', wait=True)
            break
        if "shi-de" in transcription_text or "ke-yi" in transcription_text or "en-en":
            models.generate_speech("好的，开始了", "yes.wav", cache_key="yes.wav")
            models.play_speech('yes.wav')
        else:
            models.generate_speech("好吧，你可以给我看其他东西，我会告诉你关于它们的美丽故事", "no.wav", cache_key="no.wav")
            models.play_speech('no.wav')  
            continue
        prompt = f"为儿童写一个简单的，可爱的，关于 {word}的短篇故事,100字以内，儿童大概三到七岁，没有暴力，没有恐怖，没有色情，没有政治内容。"
        story = models.generate_text(word, prompt,use_cache = False)
        print("Story:", story)

        models.generate_speech(story, story_wav_filename, cache_key=story_wav_filename,use_cache = False) # story[:10]

        models.play_speech(story_wav_filename)  
        # dalle_prompt = models.generate_text(word+"_prompt",  f"generate one line of dalle prompt for picture of this story {story}, keep it simple and sweet, its from a children story book.")
        dalle_prompt  = f"{word},{story[:50]}，可爱，大师作品, 宫崎骏画风, 全息色"
        print("Dalle Prompt:",  dalle_prompt)

        print("start the image generation")
        models.generate_image(dalle_prompt, word,use_cache = False)
        print("Image saved to", f"{word}.jpg")
        
        models.generate_speech("这里是关于故事的图片", "and_here_is.wav", cache_key="and_here_is.wav",use_cache = False) # story[:10]
        # print("speech saved to", picture_wav)
        models.play_speech("and_here_is.wav")  
        image_file_path = os.path.join(resources_path, f"{word}.jpg")
        image = cv2.imread(image_file_path)
        resized_image = cv2.resize(image, (512, 512))
        while not models.sound_queue.empty():
            time.sleep(1)
        # cv2.imshow("Image", resized_image)
        # cv2.waitKey(5000)  # You can change the time as needed
        cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('image',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow('image',resized_image)
        cv2.waitKey(100000)
        cv2.destroyAllWindows()
    except Exception as e:
        models.generate_speech("不好意思，出现了一点小问题", "error.wav", cache_key="error.wav")
        models.play_speech("error.wav", wait=True)
        print(f"An error occurred: {e}")
