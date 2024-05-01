import pyaudio
import wave
from aip import AipSpeech
import os 
import json 
import queue
import threading
import  ffmpeg
import requests
from xpinyin import Pinyin
import time 
from playaudio import play_wave_file

# modify the following to your own credentials
CLIENT_ID = "*********"
CLIENT_SECRET = "*********"

CLIENT_ID_img = "********"
CLIENT_SECRET_img = "*********"

APP_ID = "*********"
API_KEY = "*********"
SECRET_KEY = "*********"
url = "https://aip.baidubce.com/oauth/2.0/token"

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 8000
RECORD_SECONDS = 2

class BaiduAIModel:
    def __init__(self):
        self.sound_queue = queue.Queue()
        self.sound_lock = threading.Lock()
       
        params = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        self.access_token = str(
            requests.post(url, params=params).json().get("access_token")
        )
        params = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID_img,
            "client_secret": CLIENT_SECRET_img,
        }
        self.access_token_img = str(
            requests.post(url, params=params).json().get("access_token")
        )
        self.speech_client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

        self.chat_url = (
            "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token="
            + self.access_token
        )
        self.url_post = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2img?access_token=" + self.access_token_img
        self.url_ask =   "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImg?access_token=" + self.access_token_img

        self.resources_path = os.path.join(os.path.dirname(__file__), "resources")
        self.cache_file = os.path.join(self.resources_path, "cache.json")
        # read from txt file
        self.cache = self.load_cache()

    def load_cache(self):
        """Load cache from a JSON file."""
        try:
            with open(self.cache_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}  # Return an empty dictionary if there's an error loading the file

    def save_cache(self):
        """Save the current cache to a JSON file."""
        try:
            with open(self.cache_file, "w") as file:
                json.dump(self.cache, file)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def generate_chat(self, prompt):
        payload = json.dumps({"messages": [{"role": "user", "content": prompt}]})
        headers = {"Content-Type": "application/json"}
        res = requests.request("POST", self.chat_url, headers=headers, data=payload).json()
        content = res["result"]
        return content

    def generate_text(self, word, prompt, use_cache=True):
        """Generate a child-friendly story based on a word, with caching option."""
        if use_cache and word in self.cache:
            print(f"Using cached response for {word}")
            return self.cache[word]  # Return cached response if available
        try:
            story = self.generate_chat(prompt)
            self.cache[word] = story  # Cache the new response
            self.save_cache()  # Save the updated cache
            return story
        except Exception as e:
            return f"Sorry, an unexpected error occurred: {e}"

    def generate_speech(
        self, text, filename="speech.mp3", use_cache=True, cache_key=None
    ):
        """Convert text to speech and save to a file, with caching option."""
        speech_file_path = os.path.join(self.resources_path, filename)
        if use_cache and cache_key in self.cache:
            # If using cache and it exists, return path to existing file
            return f"Using cached speech file: {speech_file_path}"
        try:
            voice_stream = self.speech_client.synthesis(
                text, "zh", 6, {"vol": 15, "per": 3, "spd": 5}
            )
            with open(speech_file_path, "wb") as f:
                f.write(voice_stream)
            self.cache[cache_key] = speech_file_path  # Cache the path
            self.save_cache()  # Save the updated cache
            return f"Speech file saved successfully to {speech_file_path}"
        except Exception as e:
            return f"Sorry, an unexpected error occurred: {e}"

    def generate_image(self, prompt, word, use_cache=True, version=2):
        image_jpg = f"{word}.jpg"
        image_file_path = os.path.join(self.resources_path, image_jpg)
        if use_cache and image_jpg in self.cache:
            # If using cache and it exists, return path to existing file
            print(f"Using cached image: {image_file_path}")
            return

        # response = self.client.images.generate(
        #     model=f"dall-e-{version}",
        #     prompt=prompt,
        #     size="1024x1024",
        #     quality="standard",
        #     n=1,
        # )
        payload_post = json.dumps(
        {
            "text": prompt,
            "style": "卡通画",
            "resolution": "1024*1024",
            "num": 1,
        }
        )
        headers_post = {"Content-Type": "application/json"}
        response = requests.post(self.url_post, headers=headers_post, data=payload_post)

         # Ensure the first request was successful
        if response.status_code != 200:
            raise Exception("Error: Failed to create the task.")

        # Extract the task ID from the response JSON
        taskId = response.json().get("data", {}).get("taskId")

        if taskId is None:
            raise KeyError("Error: 'taskId' not found in the response.")
        payload_ask = json.dumps({"taskId": taskId})
        headers_ask = {"Content-Type": "application/json"}
        while True:
            response = requests.post(self.url_ask, headers=headers_ask, data=payload_ask)
            response_data = response.json()

            # Check if the 'data' key exists and retrieve 'task_status'
            data = response_data.get("data")
            status = data.get("status")
            if status != 1:
                time.sleep(1)
                continue

            imgUrls = data.get("imgUrls", [])
            if imgUrls:
                # Retrieve the first sub-task and the final_image_list
                first_img_url = imgUrls[0]
                img_url = first_img_url.get("image", [])

                if img_url:
                    image = requests.get(img_url).content
                    with open(image_file_path, "wb") as file:
                        file.write(image)
                    self.cache[image_jpg] = image_file_path  # Cache the new response
                    self.save_cache()  # Save the updated cache
                    print(f"Image saved to {word}.jpg")
                    break
                else:
                    raise KeyError(
                        "Error: 'img_url' not found in the sub_task_result_list."
                    )
            else:
                raise KeyError("Error: 'imgUrls' not found or empty.")
           

    @staticmethod
    def play_audio(sound_path):
        converted_path = str(sound_path).replace(
            ".wav", "_converted.wav"
        )  # Change the extension for the converted file        # with self.sound_lock:
        if not os.path.exists(converted_path):
            stream = ffmpeg.input(sound_path)
            stream = ffmpeg.output(
                stream, converted_path, format="wav", acodec="pcm_s16le", ar="44100"
            )
            ffmpeg.run(
                stream, overwrite_output=True, capture_stdout=True, capture_stderr=True
            )
        # winsound.PlaySound(converted_path, winsound.SND_FILENAME)
        play_wave_file(converted_path)


    def sound_player(self):
        while True:
            # Block until a sound file path is available
            sound_path = self.sound_queue.get()
            print(f"popped: {sound_path}")
            self.play_audio(sound_path)
            print(f"played: {sound_path}")
            self.sound_queue.task_done()

    def play_speech(self, filename="speech.mp3", wait=False):
        """Play a speech file from the resources directory."""
        speech_file_path = os.path.join(self.resources_path, filename)
        if wait:
            self.play_audio(speech_file_path)
            return
        try:
            print(f"pushed: {speech_file_path}")
            self.sound_queue.put(speech_file_path)  # chanage to winsound
            return
        except Exception as e:
            return f"Sorry, an unexpected error occurred: {e}"

    def transcribe_audio(self, file_path):
        with open(file_path, "rb") as audio_file:
            audio_stream = audio_file.read()

        transcription = self.speech_client.asr(audio_stream, "wav", 16000, {"dev_pid": 1536})

        if transcription["err_no"] == 0:
            pinyinresult = ""
            for t in transcription["result"]:
                pp = Pinyin()
                ptxt = pp.get_pinyin(t)
                pinyinresult += ptxt
            return pinyinresult
        else:
            print("没有识别到语音\n", result["err_no"])

    def mxrecord(self, save_path):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
        )
        stream.start_stream()
        print("* 开始录音......")

        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()

        f = wave.open(save_path, "wb")
        f.setnchannels(CHANNELS)
        f.setsampwidth(p.get_sample_size(FORMAT))
        f.setframerate(RATE)
        f.writeframes(b"".join(frames))
        f.close()