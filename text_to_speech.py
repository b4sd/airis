from google.cloud import texttospeech
from google.oauth2 import service_account
import pygame
import os

# Function to convert text to speech and save as an MP3 file
def text_to_speech(text: str, AudioFolder = "Audio", output_file: str = "output.mp3"):
    credentials = service_account.Credentials.from_service_account_file("vision_key.json")
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    # Configure text-to-speech input
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Configure voice (Vietnamese)
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    # Configure audio output
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    # Send the request and save the audio file
    response = client.synthesize_speech(
        request={"input": synthesis_input, "voice": voice, "audio_config": audio_config}
    )
    with open(os.path.join(AudioFolder, output_file), "wb") as out:
        out.write(response.audio_content)

def play_audio(file_path: str):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    print("Đang phát âm thanh...")

def pause_audio():
    try:
        pygame.mixer.music.pause()
        print("Âm thanh đã được tạm dừng.")
    except Exception as e:
        print("Không thể tạm dừng âm thanh.")

def unpause_audio():
    try:
        pygame.mixer.music.unpause()
        print("Âm thanh đã tiếp tục phát.")
    except Exception as e:
        print("Không thể tiếp tục phát âm thanh.")

def load_audio(file_path: str, start=0):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play(start=start)
    print("Đang phát âm thanh...")

def get_time():
    return pygame.mixer.music.get_pos() / 1000

def stop_audio():
    try:
        pygame.mixer.music.stop()
        print("Âm thanh đã dừng.")
    except Exception as e:
        print("Không thể dừng âm thanh.")
        
def main():
    text = """
Lịch sử thế giới là câu chuyện về sự phát triển của con người từ những buổi đầu sơ khai đến thời hiện đại. Đây không chỉ là sự ghi chép lại các sự kiện mà còn là bức tranh sống động về cách con người đã thay đổi thế giới tự nhiên và xã hội qua hàng ngàn năm. Mỗi thời kỳ lịch sử đều đánh dấu những bước tiến lớn lao và những bài học quý giá, từ thời kỳ đồ đá, các nền văn minh cổ đại, thời trung cổ, đến cuộc cách mạng công nghiệp và thế giới hiện đại.
"""
    output_file = "output.mp3"

    # Convert text to speech and save to a file
    print("Generating speech...")
    text_to_speech(text, output_file=output_file)
    print(f"Audio file saved as {output_file}")
    output_file = os.path.join("Audio", output_file)
    
    while True:
        command = input("Enter command (play/stop/exit): ").strip().lower()
        if command == "play":
            play_audio(output_file)
        elif command == "stop":
            stop_audio()
        elif command == "exit":
            stop_audio()
            pygame.mixer.quit()
            break
        elif command == "pause":
            pause_audio()
        elif command == "unpause":
            unpause_audio()
        else:
            print("Invalid command. Use 'play', 'stop', or 'exit'.")

if __name__ == "__main__":
    main()