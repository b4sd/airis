from google.cloud import texttospeech
from google.oauth2 import service_account
import pygame

# Function to convert text to speech and save as an MP3 file
def text_to_speech(text: str, output_file: str = "output.mp3"):
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
    with open(output_file, "wb") as out:
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

1. Thời kỳ tiền sử và sự xuất hiện của loài người
Thời kỳ tiền sử là giai đoạn mà con người chưa có chữ viết, kéo dài hàng triệu năm. Trong thời kỳ này, tổ tiên của chúng ta đã phát triển từ loài vượn người (Australopithecus) thành Homo sapiens. Những khám phá khảo cổ học cho thấy người tiền sử đã học cách sử dụng công cụ, phát minh ra lửa và sống thành từng nhóm để săn bắt và hái lượm.

Sự chuyển đổi lớn xảy ra trong Cuộc cách mạng nông nghiệp (khoảng 10.000 năm TCN), khi con người bắt đầu trồng trọt và chăn nuôi. Điều này dẫn đến sự hình thành của các cộng đồng định cư đầu tiên, như tại vùng Lưỡng Hà, thung lũng sông Nile, và lưu vực sông Ấn.

2. Sự hình thành các nền văn minh cổ đại
Các nền văn minh cổ đại đánh dấu bước phát triển vượt bậc trong tổ chức xã hội, nghệ thuật, và khoa học. Ở Lưỡng Hà, con người đã phát minh ra chữ viết hình nêm và xây dựng những thành phố lớn như Babylon. Ở Ai Cập cổ đại, các kim tự tháp là biểu tượng cho sự phát triển về kiến trúc và niềm tin tôn giáo sâu sắc vào thế giới bên kia.

Ở Ấn Độ, nền văn minh lưu vực sông Ấn phát triển mạnh mẽ, với các thành phố như Harappa và Mohenjo-daro. Trong khi đó, Trung Quốc cổ đại đã xây dựng nền văn minh lâu đời với các triều đại Hạ, Thương, Chu, và những tiến bộ vượt bậc trong nông nghiệp, giấy, và nghệ thuật.

3. Thời kỳ cổ điển và đế chế lớn
Thời kỳ cổ điển chứng kiến sự ra đời của những đế chế và nền văn hóa có ảnh hưởng sâu sắc đến thế giới ngày nay. Hy Lạp cổ đại đã đóng góp nhiều vào triết học, nghệ thuật, và khoa học, với các tên tuổi nổi tiếng như Socrates, Plato, và Aristotle. Đế chế La Mã tiếp tục xây dựng trên nền tảng đó, mở rộng lãnh thổ khắp châu Âu và Bắc Phi, đồng thời phát triển luật pháp và kỹ thuật xây dựng như cầu cống và đường xá.

Ở châu Á, đế chế Maurya và đế chế Gupta tại Ấn Độ đã thiết lập các triều đại vàng son, đưa Phật giáo và Hindu giáo lan rộng. Đế chế Hán tại Trung Quốc là một trong những thời kỳ thịnh vượng nhất, nổi bật với con đường tơ lụa và các phát minh như la bàn và giấy.
"""
    output_file = "output.mp3"

    # Convert text to speech and save to a file
    print("Generating speech...")
    text_to_speech(text, output_file)
    print(f"Audio file saved as {output_file}")

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