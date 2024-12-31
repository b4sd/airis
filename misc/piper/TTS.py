import os
import subprocess
import eng_to_ipa as ipa
import json
import re
import pyphen

# vi_VN-25hours_single-low.onnx
# vi_VN-vais1000-medium.onnx
# finetuning_pretrained_vi.onnx

class TTSProcessor:
    def __init__(self, vocab_filename, model_filename="finetuning_pretrained_vi.onnx", output_filename="output.wav"):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Paths for vocabulary, model, and output files
        self.vocab_path = os.path.join(self.script_dir, vocab_filename)
        self.model_path = model_filename
        self.output_path = output_filename

        # Initialize Pyphen
        self.en_dic = pyphen.Pyphen(lang='en')

        # TTS parameters
        self.sentence_silence = 1
        self.length_scale = 2

        # Initialize Vietnamese checker
        self.vn_checker = self.VNChecker(self.vocab_path, self)

    def split_syllables(self, text):
        return self.en_dic.inserted(text)

    def keep_vietnamese(self, text):
        viet_lowercase = "áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ"
        text = text.lower()
        return ''.join([c for c in text if c in viet_lowercase or c.isalpha() or c.isspace() or c.isdigit()])

    def fix_to_json(self, data):
        # Replace single quotes with double quotes for valid JSON strings
        data = re.sub(r"'", '"', data)
        # Add double quotes around keys (like `ipa` or `vie`) that are not quoted
        data = re.sub(r"(\w+):", r'"\1":', data)
        # Replace `[Object]` with null
        data = re.sub(r"\[Object\]", "null", data)
        return json.loads(data)

    def ipa2vn(self, text):
        text = text.replace("r", "ɹ")
        text = text.replace("ʤ", "dʒ")
        text = text.replace("ʧ", "tʃ")
        text = text.replace("g", "ɡ")
        print("Converting", text)
        # Run Node.js subprocess and capture output

        # Subprocess directory is the script directory
        os.chdir(self.script_dir)

        start_text = text

        result = subprocess.run(['node', 'ipa_to_vn.js', text], stdout=subprocess.PIPE, text=True, encoding='utf-8')
        result = result.stdout.strip()
        result = self.fix_to_json(result)
        print("IPA to VN", start_text, result[0]['vie'])
        return result[0]['vie']

    class VNChecker:
        def __init__(self, vocabulary_path, parent_instance):
            self.data = set()
            self.parent_instance = parent_instance  # Store the parent instance (TTSProcessor)
            delim = r' -,.;:!?()'
            with open(vocabulary_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    line = [TTSProcessor.keep_vietnamese(None, word) for word in re.split(f'[{delim}]', line) if word]
                    for word in line:
                        self.data.add(word)

        def check(self, word):
            word = TTSProcessor.keep_vietnamese(None, word)
            return word in self.data

        def to_vn(self, word):
            new_word = TTSProcessor.keep_vietnamese(None, word)
            if self.check(new_word.lower()):
                return word
            
            # try:
            #     ipa_word = ipa.convert(new_word)
            #     print("To IPA", new_word, ipa_word)
            #     # Use the parent instance to call ipa2vn
            #     return self.parent_instance.ipa2vn(ipa_word).replace('-', ' ')
            # except Exception as e:
            #     print("Error converting", new_word, e)
                
            try:
                return self.parent_instance.split_syllables(new_word).replace('-', ' ')
            except Exception as e:
                print("Error splitting", new_word, e)
            
            
            return word

        def sentence_to_vn(self, sentence):
            sentence = sentence.replace('\n', ' ')
            sentence = sentence.replace('\t', ' ')
            sentence = sentence.replace(':', '.')
            sentence = sentence.strip()
            print(sentence)
            return ' '.join([self.to_vn(word) for word in sentence.split(' ')])
        
    def to_speech(self, text, output_file="output.wav"):
        text = text.replace('\n', ' ')
        text = self.vn_checker.sentence_to_vn(text)

        # Set run echo in the right directory
        os.chdir(self.script_dir)

        command = f'echo "{text}" | .\\piper.exe -m {self.model_path} -f {output_file} --length_scale {self.length_scale} --sentence_silence {self.sentence_silence}'
        print(command)
        os.system(command)

    def remove_audio_files(self, path):
        path = os.path.join(self.script_dir, path)
        for file in os.listdir(path):
            if file.endswith(".wav"):
                os.remove(os.path.join(path, file))

# tts = TTSProcessor("Viet74K.txt")
# print("Harry ", tts.vn_checker.to_vn("Harry"))
# print("Potter ", tts.vn_checker.to_vn("Potter"))
# print("Hermione ", tts.vn_checker.to_vn("Hermione"))
# print("Granger ", tts.vn_checker.to_vn("Granger"))
# print("Ron ", tts.vn_checker.to_vn("Ron"))
# print("Weasley ", tts.vn_checker.to_vn("Weasley"))

# # To vn
# harry = "Harry"
# harry = ipa.convert(harry)
# print("Harry ", harry, tts.ipa2vn(harry))
