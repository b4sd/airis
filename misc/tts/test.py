# import torch
# from TTS.api import TTS

# # Get device
# device = "cuda" if torch.cuda.is_available() else "cpu"

# # Init TTS with the target model name
# tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False)

# # Run TTS
# tts.tts_to_file(text="Ich bin eine Testnachricht.", file_path="output.wav")

# import os

# import torch

# from huggingface_hub import snapshot_download
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import Xtts


# snapshot_download(repo_id="capleaf/viXTTS",
#                   repo_type="model",
#                   local_dir="model")

# config = XttsConfig()
# config.load_json("./model/config.json")
# XTTS_MODEL = Xtts.init_from_config(config)
# XTTS_MODEL.load_checkpoint(config, checkpoint_dir="./model/")
# XTTS_MODEL.eval()
# if torch.cuda.is_available():
#     XTTS_MODEL.cuda()

# gpt_cond_latent, speaker_embedding = XTTS_MODEL.get_conditioning_latents(
#     audio_path="./model/vi_sample.wav",
#     gpt_cond_len=XTTS_MODEL.config.gpt_cond_len,
#     max_ref_length=XTTS_MODEL.config.max_ref_len,
#     sound_norm_refs=XTTS_MODEL.config.sound_norm_refs,
# )


# import time
# start = time.time()
# out_wav = XTTS_MODEL.inference(
#     text="Xin chào, tôi là một công cụ có khả năng chuyển đổi văn bản thành giọng nói tự nhiên, được phát triển bởi nhóm Nón lá",
#     language="vi",
#     gpt_cond_latent=gpt_cond_latent,
#     speaker_embedding=speaker_embedding,
#     temperature=0.3,
#     length_penalty=1.0,
#     repetition_penalty=10.0,
#     top_k=30,
#     top_p=0.85,
# )
# out_wav = XTTS_MODEL.inference(
#     text="Xin chào, tôi là một công cụ có khả năng chuyển đổi văn bản thành giọng nói tự nhiên, được phát triển bởi nhóm Nón lá",
#     language="vi",
#     gpt_cond_latent=gpt_cond_latent,
#     speaker_embedding=speaker_embedding,
#     temperature=0.3,
#     length_penalty=1.0,
#     repetition_penalty=10.0,
#     top_k=30,
#     top_p=0.85,
# )
# out_wav = XTTS_MODEL.inference(
#     text="Xin chào, tôi là một công cụ có khả năng chuyển đổi văn bản thành giọng nói tự nhiên, được phát triển bởi nhóm Nón lá",
#     language="vi",
#     gpt_cond_latent=gpt_cond_latent,
#     speaker_embedding=speaker_embedding,
#     temperature=0.3,
#     length_penalty=1.0,
#     repetition_penalty=10.0,
#     top_k=30,
#     top_p=0.85,
# )
# print(f"Time: {time.time() - start}")
# import IPython.display as ipd
# ipd.Audio(out_wav["wav"], rate=24000)

# # to file
# from scipy.io.wavfile import write
# write("output.wav", 24000, out_wav["wav"])
