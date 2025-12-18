
import cv2
import numpy as np
import wave
from PIL import Image
import os

class Steganography:
    def encode_image(self, input_image_path, message, output_image_path):
        image = Image.open(input_image_path)
        encoded = image.copy()
        width, height = image.size
        message += chr(0)  # Null character as delimiter
        data = ''.join(format(ord(c), '08b') for c in message)
        idx = 0

        for y in range(height):
            for x in range(width):
                if idx >= len(data):
                    break
                pixel = list(encoded.getpixel((x, y)))
                for i in range(3):  # RGB channels
                    if idx < len(data):
                        pixel[i] = pixel[i] & ~1 | int(data[idx])
                        idx += 1
                encoded.putpixel((x, y), tuple(pixel))
            if idx >= len(data):
                break

        encoded.save(output_image_path)

    def decode_image(self, input_image_path):
        image = Image.open(input_image_path)
        width, height = image.size
        data = ""
        for y in range(height):
            for x in range(width):
                pixel = list(image.getpixel((x, y)))
                for i in range(3):
                    data += str(pixel[i] & 1)
        chars = [chr(int(data[i:i+8], 2)) for i in range(0, len(data), 8)]
        message = ''.join(chars)
        return message.split(chr(0))[0]

    def encode_audio(self, input_audio_path, message, output_audio_path):
        with wave.open(input_audio_path, 'rb') as audio:
            params = audio.getparams()
            frames = bytearray(list(audio.readframes(audio.getnframes())))
        
        message += chr(0)
        data = ''.join(format(ord(c), '08b') for c in message)
        if len(data) > len(frames):
            raise ValueError("Message too large to encode in audio file.")
        
        for i in range(len(data)):
            frames[i] = frames[i] & 254 | int(data[i])
        
        with wave.open(output_audio_path, 'wb') as audio:
            audio.setparams(params)
            audio.writeframes(frames)

    def decode_audio(self, input_audio_path):
        with wave.open(input_audio_path, 'rb') as audio:
            frames = bytearray(list(audio.readframes(audio.getnframes())))
        data = ''.join([str(frame & 1) for frame in frames])
        chars = [chr(int(data[i:i+8], 2)) for i in range(0, len(data), 8)]
        message = ''.join(chars)
        return message.split(chr(0))[0]

    def encode_text(self, input_text_path, message, output_text_path):
        with open(input_text_path, 'r') as f:
            content = f.read()
        hidden_message = ''.join([char + '​' for char in message])  # Add zero-width space
        content += '
' + hidden_message + '‌'  # End delimiter
        with open(output_text_path, 'w') as f:
            f.write(content)

    def decode_text(self, input_text_path):
        with open(input_text_path, 'r') as f:
            content = f.read()
        if '‌' in content:
            hidden = content.split('‌')[0].split('
')[-1]
            message = ''.join([hidden[i] for i in range(0, len(hidden), 2)])
            return message
        return ""

    def encode_video(self, input_video_path, message, output_video_path):
        cap = cv2.VideoCapture(input_video_path)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        message += chr(0)
        data = ''.join(format(ord(c), '08b') for c in message)
        idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            for y in range(frame.shape[0]):
                for x in range(frame.shape[1]):
                    for c in range(3):
                        if idx < len(data):
                            frame[y, x, c] = frame[y, x, c] & ~1 | int(data[idx])
                            idx += 1
            out.write(frame)
            if idx >= len(data):
                break

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        cap.release()
        out.release()

    def decode_video(self, input_video_path):
        cap = cv2.VideoCapture(input_video_path)
        data = ""
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            for y in range(frame.shape[0]):
                for x in range(frame.shape[1]):
                    for c in range(3):
                        data += str(frame[y, x, c] & 1)
        cap.release()
        chars = [chr(int(data[i:i+8], 2)) for i in range(0, len(data), 8)]
        message = ''.join(chars)
        return message.split(chr(0))[0]
