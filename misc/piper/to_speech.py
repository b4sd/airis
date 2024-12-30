import os
import subprocess
import eng_to_ipa as ipa
import json
import re
import pyphen

import sys

# Get the absolute path of the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the 'misc/piper' directory to the sys.path relative to the script's directory
sys.path.append(os.path.join(script_dir, 'misc', 'piper'))

sentence_silence = 1
length_scale = 2
en_dic = pyphen.Pyphen(lang='en')

def split_syllables(text):
    return en_dic.inserted(text)

def keep_vietnamese(text):
    viet_lowercase = "áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ"
    text = text.lower()
    return ''.join([c for c in text if c in viet_lowercase or c.isalpha() or c.isspace() or c.isdigit()])


def fix_to_json(data):
    # Replace single quotes with double quotes for valid JSON strings
    data = re.sub(r"'", '"', data)
    # Add double quotes around keys (like `ipa` or `vie`) that are not quoted
    data = re.sub(r"(\w+):", r'"\1":', data)
    # Replace `[Object]` with null
    data = re.sub(r"\[Object\]", "null", data)
    return json.loads(data)

def ipa2vn(text):
    text = fr"/{text}/"
    print("Converting", text)
    # replace specific characters
    # " ", "/", "a", "aɪ", "aʊ", "b", "d", "dʒ", "e", "eɪ", "eɪn", "eɪt", "f", "h", "i", "j", "jaʊ", "jeɪ", "ji", "joʊ", "ju", "jæ", "jɑ", "jɔ", "jə", "jəŋ", "jɛ", "jɪ", "jʊ", "k", "m", "n", "o", "oʊ", "p", "s", "t", "tɹ", "tʃ", "u", "v", "w", "z", "æ", "ð", "ŋ", "ɑ", "ɔ", "ɔɪ", "ə", "əj", "ɛ", "ɝ", "ɡ", "ɪ", "ɫ", "ɹ", "ʃ", "ʊ", "ʒ", "ˈ", "ˌ", "θ", or end of input
    text = text.replace("r", "ɹ")
    text = text.replace("ʤ", "dʒ")
    text = text.replace("ʧ", "tʃ")
    text = text.replace("g", "ɡ")
    # Run Node.js subprocess and capture output
    result = subprocess.run(['node', 'ipa_to_vn.js', text], stdout=subprocess.PIPE, text=True, encoding='utf-8')
    result = result.stdout.strip()
    # Convert to JSON
    result = fix_to_json(result)
    # return text
    return result[0]['vie']

class vn_checker:
    def __init__(self, vocabulary_path):
        self.data = set()
        # Delimiters for splitting text
        delim = r' -,.;:!?()'
        with open(vocabulary_path, 'r', encoding='utf-8') as f:  # Ensure UTF-8 encoding
            for line in f:
                line = line.strip()
                # Split and clean words
                line = [keep_vietnamese(word) for word in re.split(f'[{delim}]', line) if word]
                for word in line:
                    self.data.add(word)

    def check(self, word):
        # Remove all non-alphabet characters and check if the word exists in the vocabulary
        word = keep_vietnamese(word)
        # if word.isalnum():
        #     return True
        # print("Checking ", word, word in self.data)
        # data is set
        return word in self.data
    
    def to_vn(self, word):
        # Remove all non-alphabet characters
        print("Converting", word)
        new_word = keep_vietnamese(word)
        print("New word", new_word)
        
        if self.check(new_word.lower()):
            return word
        # return ipa2vn(ipa.convert(new_word))
        return split_syllables(new_word)
    
    def sentence_to_vn(self, sentence):
        # Convert each word in the sentence to Vietnamese
        sentence = sentence.replace('\n', ' ')
        sentence = sentence.strip()
        print(sentence)
        return ' '.join([self.to_vn(word) for word in sentence.split(' ')])
    
# Initialize the checker with the vocabulary file
print(os.path.join(script_dir, 'vietnamese_vocab.txt'))
vn_checker = vn_checker(os.path.join(script_dir, 'vietnamese_vocab.txt'))

def to_speech(text, model_path = "vi_VN-vais1000-medium.onnx", output_path = "output.wav"):
    text = text.replace('\n', ' ')
    # Convert text to Vietnamese
    text = vn_checker.sentence_to_vn(text)
    # Run the piper TTS engine

    model_path = os.path.join(script_dir, model_path)
    output_path = os.path.join(script_dir, output_path)

    print(f'echo "{text}" | .\\piper.exe -m {model_path} -f {output_path} --length_scale {length_scale} --sentence_silence {sentence_silence}')
    os.system(f'echo "{text}" | .\\piper.exe -m {model_path} -f {output_path} --length_scale {length_scale} --sentence_silence {sentence_silence}')

