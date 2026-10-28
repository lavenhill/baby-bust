"""R4-4a: head boxes for the poster images, used at run time to keep poster text off faces.
usage: python3 tools/heads.py            -> writes tools/heads.json
Needs: pip install opencv-python-headless pillow; downloads the YuNet face model (OpenCV Zoo, MIT) on first run.
Each detected face box (x,y,w,h in the 960x640 poster) is grown into a head box that includes hair:
  width 1.5x (centred), top raised by 0.45 x face height, height 1.55x. Output is normalised to 0..1.
Faces narrower than MIN_FACE px (tiny background figures, also YuNet's false hits on texture) are ignored.
Manual overrides (extra boxes to avoid, preferred text top) live in content_zh.py POSTER_TEXT, not here."""
import os, glob, json, urllib.request
import cv2, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join('/tmp', 'face_detection_yunet_2023mar.onnx')
MIN_FACE = 30
URL = 'https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx'

def head_box(x, y, w, h, W=960, H=640):
    """face box (px) -> head box normalised to the poster; clipped to the image."""
    hx, hy, hw, hh = x + w / 2 - .75 * w, y - .45 * h, 1.5 * w, 1.55 * h
    x0, y0, x1, y1 = max(0, hx), max(0, hy), min(W, hx + hw), min(H, hy + hh)
    return [round(x0 / W, 4), round(y0 / H, 4), round((x1 - x0) / W, 4), round((y1 - y0) / H, 4)]

def main():
    if not os.path.exists(MODEL): urllib.request.urlretrieve(URL, MODEL)
    yn = cv2.FaceDetectorYN.create(MODEL, '', (960, 640), 0.5, 0.3, 5000)
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, '..', 'img', '*_poster.webp'))):
        im = cv2.cvtColor(np.array(Image.open(f).convert('RGB')), cv2.COLOR_RGB2BGR); H, W = im.shape[:2]
        yn.setInputSize((W, H)); _, F = yn.detect(im)
        k = os.path.basename(f).replace('_poster.webp', '')
        out[k] = [head_box(*[int(v) for v in r[:4]], W=W, H=H) for r in (F if F is not None else []) if r[2] >= MIN_FACE]
    json.dump(out, open(os.path.join(HERE, 'heads.json'), 'w'), separators=(',', ':'))
    print({k: len(v) for k, v in out.items()})

if __name__ == '__main__': main()
