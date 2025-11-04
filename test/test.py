import whisperx
import torch

# 1. 自动检测设备
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# 2. 加载 Whisper 模型（选择 base / small / medium / large-v2）
compute_type = "float16" if device.startswith("cuda") else "float32"
model = whisperx.load_model("small", device=device, compute_type=compute_type)

# 3. 执行语音识别
audio_file = "audio.mp3"
result = model.transcribe(audio_file)

print("Detected language:", result["language"])
print("Segments before alignment:", len(result["segments"]))

# 4. 对齐（提高时间精度）
model_a, metadata = whisperx.load_align_model(
    language_code=result["language"], device=device
)
aligned_result = whisperx.align(
    result["segments"], model_a, metadata, audio_file, device
)

# 5. 输出结果
for seg in aligned_result["segments"]:
    print(f"[{seg['start']:.2f}s -> {seg['end']:.2f}s] {seg['text']}")
