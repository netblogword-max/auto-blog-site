import os
import random
from datetime import datetime
import requests
import subprocess
from dotenv import load_dotenv  # <--- Tambahkan ini

# Load variabel dari file .env
load_dotenv()

# ===== CONFIG =====
ARTICLES_DIR = os.path.join(os.getcwd(), "articles")
IMAGES_DIR = os.path.join(os.getcwd(), "images")
HISTORY_FILE = os.path.join(os.getcwd(), "history.txt")

# Ambil key dari environment variable
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIT_BRANCH = "main"


# ===== CREATE FOLDERS IF NOT EXIST =====
os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
if not os.path.exists(HISTORY_FILE):
    open(HISTORY_FILE, "w").close()

def fetch_unsplash_image(topic):
    # Membersihkan judul untuk pencarian gambar yang lebih baik
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

def generate_article(title):
    print(f"[PROCESS] Menghasilkan konten AI untuk: {title}...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"Buatlah artikel blog yang sangat mendalam, menarik, dan informatif dalam bahasa Indonesia tentang: {title}. Gunakan format paragraf yang rapi, sertakan sub-judul (H2), dan buat minimal 500 kata."
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Anda adalah blogger profesional yang ahli dalam menulis konten berkualitas tinggi dan SEO friendly."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        result = r.json()
        content = result['choices'][0]['message']['content']
        # Mengubah markdown sederhana atau newline menjadi tag HTML
        return content.replace("\n", "<br>")
    except Exception as e:
        print(f"[ERROR] Groq API bermasalah: {e}")
        return "Konten gagal dihasilkan karena kendala teknis."

def save_article(title, content, image_file):
    safe_title = title.replace(" ", "_").replace(":", "").replace("&", "and")
    random_id = random.randint(1000, 9999)
    filename = os.path.join(ARTICLES_DIR, f"{safe_title}_{random_id}.html")
    
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        img {{ width: 100%; height: auto; border-radius: 8px; margin-bottom: 20px; }}
        h1 {{ color: #2c3e50; }}
        .content {{ text-align: justify; }}
        .nav {{ margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }}
        a {{ color: #3498db; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {"<img src='../images/" + image_file + "'>" if image_file else ""}
    <div class="content">
        {content}
    </div>
    <div class="nav">
        <p>Kembali ke: <a href="index.html">Daftar Artikel</a></p>
    </div>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {title}\n")
    return filename

def generate_index():
    files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html") and f != "index.html"]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(ARTICLES_DIR, x)), reverse=True)
    
    html = """<html><head><title>Blog Saya</title><style>
    body { font-family: sans-serif; max-width: 600px; margin: 50px auto; line-height: 1.6; }
    li { margin-bottom: 10px; }
    </style></head><body>
    <h1>Daftar Artikel Terbaru</h1><ul>"""
    
    for file in files:
        display_title = file.replace("_", " ").replace(".html", "")
        html += f'<li><a href="{file}">{display_title}</a></li>\n'
    
    html += "</ul></body></html>"
    
    with open(os.path.join(ARTICLES_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("[SUCCESS] Index diperbarui.")

def commit_push_github():
    print("[PROCESS] Melakukan push ke GitHub...")
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Auto update artikel {datetime.now()}"])
    subprocess.run(["git", "push", "origin", GIT_BRANCH])
    print("[SUCCESS] Selesai! Cek situs Netlify kamu dalam 1 menit.")

if __name__ == "__main__":
    topics = ["Gaya Hidup Digital", "AI & Automation", "Masa Depan Teknologi", "Tips Produktivitas"]
    
    # Menghasilkan 2 artikel
    for _ in range(2):
        chosen_topic = random.choice(topics)
        title = f"{chosen_topic}: Tren Masa Kini"
        content = generate_article(title)
        image_file = fetch_unsplash_image(chosen_topic)
        save_article(title, content, image_file)
    
    generate_index()
    commit_push_github()

