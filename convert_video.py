import cv2
import os

video_map = {
    "chest":    "videos/chest/1.MOV",
    "cough":    "videos/cough/1.MOV",
    "breath":   "videos/breath/1.MOV",
    "pain":     "videos/pain/1.MOV",
    "vomit":    "videos/vomit/1.MOV",
    "ear":      "videos/ear/1.MOV",
    "eye":      "videos/eye/1.MOV",
    "medicine": "videos/medicine/1.MOV",
    "hurt":     "videos/hurt/1.MOV",
    "sick":     "videos/sick/1.MOV",
    "chest":    "videos/chest/1.MOV",
    "cough":    "videos/cough/1.MOV",
    "pain":     "videos/pain/1.MOV",
    "vomit":    "videos/vomit/1.MOV",
    "ear":      "videos/ear/1.MOV",
    "head":     "videos/head/1.MOV",
    "eye":      "videos/eye/1.MOV",
    "medicine": "videos/medicine/1.MOV",
    "hurt":     "videos/hurt/1.MOV",
    "sick":     "videos/sick/1.MOV",
    "fever":    "videos/fever/1.MOV",
    "throat":   "videos/throat/1.MOV",
    "surgery":  "videos/surgery/1.MOV",
    "emergency": "videos/emergency/1.MOV",
    "injection": "videos/injection/1.MOV",
    "relax": "videos/relax/1.MOV",
    "dizzy": "videos/dizzy/1.MOV",
    "tired": "videos/tired/1.MOV",
    "help": "videos/help/1.MOV",
    "doctor": "videos/doctor/1.MOV",
    "pregnant": "videos/pregnant/1.MOV",
    "headache": "videos/headache/1.MOV",
    "hello":"videos/hello/1.MOV",
    "throat": "videos/throat/1.MOV",
    "back": "videos/back/1.MOV",
    "thank_you": "videos/thank_you/1.MOV",
}

for label, mov_path in video_map.items():
    mp4_path = mov_path.replace(".MOV", ".mp4")

    if not os.path.exists(mov_path):
        print(f"[SKIP] Not found: {mov_path}")
        continue

    cap = cv2.VideoCapture(mov_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(mp4_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

    print(f"Converting {label}...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    print(f"[DONE] Saved: {mp4_path}")

print("\nAll conversions complete!")