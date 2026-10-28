"""Contact sheet of storyboard stills: python sheet.py e1 0.6,3.2,... -> work/<key>_sheet.jpg"""
import sys
from PIL import Image
k, ts = sys.argv[1], sys.argv[2].split(",")
ims = [Image.open(f"work/{k}_{float(t)}.jpg").resize((270, 480)) for t in ts]
cols = 7; rows = (len(ims) + cols - 1) // cols
out = Image.new("RGB", (270 * cols, 480 * rows), "white")
for i, im in enumerate(ims): out.paste(im, ((i % cols) * 270, (i // cols) * 480))
out.save(f"work/{k}_sheet.jpg", quality=82)
