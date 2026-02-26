import os
import random
from datetime import datetime
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

# ===== CONFIG =====
ARTICLES_DIR = os.path.join(os.getcwd(), "articles")
IMAGES_DIR = os.path.join(os.getcwd(), "images")
HISTORY_FILE = os.path.join(os.getcwd(), "history.txt")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIT_BRANCH = "main"

os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def get_ai_topic():
    """AI memikirkan topik artikel yang menarik dan unik"""
    print("[PROCESS] AI sedang memikirkan ide topik hari ini...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # Prompt agar AI mencari topik yang beragam
    prompt = "Berikan satu judul artikel blog yang unik, sedang tren, dan menarik tentang teknologi, gaya hidup digital, atau AI. Berikan HANYA judulnya saja, tanpa tanda petik atau penjelasan."
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1.0 # Kreativitas maksimal agar topik selalu beda
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        topic = r.json()['choices'][0]['message']['content'].strip()
        return topic
    except:
        return f"Tren Teknologi {random.randint(100, 999)}"

def generate_article(title):
    styles = ["edukatif", "santai/slang", "profesional", "storytelling", "opini tajam"]
    chosen_style = random.choice(styles)
    
    print(f"[PROCESS] Menulis artikel gaya {chosen_style}: {title}")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    prompt = (
        f"Buat artikel blog mendalam tentang: {title}. "
        f"Gunakan gaya bahasa {chosen_style}. "
        f"Gunakan format HTML: <h2> untuk sub-judul, <p> untuk paragraf. "
        f"Minimal 600 kata. Pastikan isinya unik dan belum pernah ditulis sebelumnya."
    )
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "Anda adalah blogger kreatif kelas dunia."}, {"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=60)
        content = r.json()['choices'][0]['message']['content']
        return content.replace("\n", "<br>")
    except:
        return "Gagal generate konten."

# ... (fungsi fetch_unsplash_image, save_article, generate_index, commit_push_github tetap sama)

def fetch_unsplash_image(topic):
    search_query = topic.split(":")[0] 
    url = f"https://api.unsplash.com/photos/random?query={search_query}&client_id={UNSPLASH_ACCESS_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img_url = data["urls"]["regular"]
            filename = f"img_{random.randint(1000, 9999)}.jpg"
            filepath = os.path.join(IMAGES_DIR, filename)
            img_data = requests.get(img_url).content
            with open(filepath, "wb") as f:
                f.write(img_data)
            return filename
    except:
        pass
    return ""

def save_article(title, content, image_file):
    safe_title = title.replace(" ", "_").replace(":", "").replace("&", "and")
    random_id = random.randint(1000, 9999)
    filename = os.path.join(ARTICLES_DIR, f"{safe_title}_{random_id}.html")
    html = f"<html><head><title>{title}</title><style>body{{font-family:sans-serif;max-width:800px;margin:auto;padding:20px;line-height:1.6}} img{{width:100%}}</style></head><body><h1>{title}</h1>"
    if image_file: html += f"<img src='../images/{image_file}'>"
    html += f"<div>{content}</div><hr><a href='index.html'>Kembali</a></body></html>"
    with open(filename, "w", encoding="utf-8") as f: f.write(html)
    return filename

def generate_index():
    files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html") and f != "index.html"]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(ARTICLES_DIR, x)), reverse=True)
    html = "<html><head><title>Blog AI</title></head><body><h1>Artikel Terbaru</h1><ul>"
    for file in files:
        title = file.replace("_", " ").replace(".html", "")
        html += f'<li><a href="{file}">{title}</a></li>'
    html += "</ul></body></html>"
    with open(os.path.join(ARTICLES_DIR, "index.html"), "w", encoding="utf-8") as f: f.write(html)

def commit_push_github():
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Auto post {datetime.now()}"])
    subprocess.run(["git", "push", "origin", GIT_BRANCH])

if __name__ == "__main__":
    # AI mencari 2 topik berbeda setiap kali dijalankan
    for _ in range(2):
        title = get_ai_topic()
        content = generate_article(title)
        image_file = fetch_unsplash_image(title)
        save_article(title, content, image_file)
    
    generate_index()
    commit_push_github()
