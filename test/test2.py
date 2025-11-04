
import whisper

model = whisper.load_model("small")  # 可用 tiny / base / small / medium / large
result = model.transcribe("audio.mp3")

for seg in result["segments"]:
    print(f"[{seg['start']:.2f}s → {seg['end']:.2f}s] {seg['text']}")
