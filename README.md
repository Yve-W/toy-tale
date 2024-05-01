# toy-tale
# Interactive Storytelling System with Object Detection

This project integrates multiple functionalities to create an interactive storytelling system. It uses object detection, text-to-speech, audio transcription, and image generation to deliver a unique experience to users. The system can detect objects, translate them into another language, play audio, record voice input, and generate corresponding images.

## Features

- **Serial Communication**: Reads data from a pressure sensor connected via a serial port.
- **Object Detection**: Detects objects and translates them.
- **Text-to-Speech**: Converts text to spoken words.
- **Audio Recording**: Records audio input from the user.
- **Speech-to-Text**: Converts recorded audio to text for further processing.
- **Story Generation**: Generates short stories based on detected objects.
- **Image Generation**: Creates images related to the generated story.
- **GUI Display**: Displays generated images in full screen.

##Usage
Setup Hardware: Connect your hardware (Arduino, sensors, etc.) to your computer.
Identify Serial Port: Use ls /dev/tty* to identify your serial port. Update the code if necessary.
Modify Api with Your Own Credential:In [model_cn.py](story_teller/model_cn.py),use your own credential.
press the pressure sensor then the project will start!
