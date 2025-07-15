# RetroDiffusion Expression Generator

A tiny helper that creates a bunch of facial expressions from a single input image.
<img width="1344" height="1024" alt="Sheet" src="https://github.com/user-attachments/assets/48e81145-a053-4a72-9104-ac3c4ba8e933" />

---

## 1. Grab an API key

1. Sign in here: <https://www.retrodiffusion.ai/app/devtools>  
2. Click the + icon next to "API Keys" and copy it  
3. **Either**  
   * paste the key into the file named  
     `Write API key in here.txt` (same folder as `generate.py`)  
   **or**  
   * set an env var once per shell session  
     ```bash
     export RD_API_KEY=rdpk_your_key_here
     ```

---

## 2. Python setup

```bash
python 3.9+
pip install requests pillow
```

3. Run the script

```python
python generate.py -i INPUT_IMAGE -o OUTPUT_DIR
```

Flag	What it does
-i --input	Path to a PNG or JPG that is 16 to 256 pixels on each side
-o --output	Folder for the results. Defaults to "outputs"

Example:

python generate.py -i face.png -o outputs

The folder will end up with all the expression files:

```
outputs/
├─ smile.png
├─ frown.png
...
└─ excited.png
```
