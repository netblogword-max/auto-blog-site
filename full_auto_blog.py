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
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIT_BRANCH = "main"

os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def get_ai_topic():
    """AI memikirkan topik artikel yang sangat spesifik dan menarik"""
    print("[PROCESS] AI sedang meriset topik tren untuk Anda...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    prompt = "Berikan satu judul artikel blog yang sangat spesifik tentang Teknologi masa depan, Tutorial AI, atau Strategi Digital Marketing. Judul harus memancing rasa ingin tahu. Berikan HANYA judul tanpa tanda petik."
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1.0
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        return r.json()['choices'][0]['message']['content'].strip()
    except:
        return f"Inovasi Digital Terbaru {random.randint(100, 999)}"

def generate_article(title):
    """Menghasilkan artikel mendalam 2000-3000 kata dengan format HTML"""
    styles = ["Analisis Teknis Mendalam", "Panduan Langkah-demi-Langkah", "Opini Pakar Strategis", "Eksperimen Storytelling"]
    chosen_style = random.choice(styles)
    
    print(f"[PROCESS] Menulis artikel 3000 kata dengan gaya: {chosen_style}")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    prompt = (
        f"Tulislah artikel blog yang sangat lengkap dan mendalam tentang: {title}. "
        f"Gunakan gaya penulisan {chosen_style}. "
        f"SYARAT WAJIB: "
        f"1. Panjang artikel minimal 2500-3000 kata. "
        f"2. Berikan penjelasan detail setiap poin. "
        f"3. Sertakan panduan praktis atau tutorial langkah-demi-langkah. "
        f"4. Gunakan format HTML: <h2> dan <h3> untuk judul bagian, <p> untuk paragraf, <strong> untuk poin penting, dan <ul><li> untuk daftar. "
        f"Jangan menulis konten pendek atau berulang. Berikan kualitas terbaik Anda."
    )
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Anda adalah jurnalis teknologi senior yang menulis konten pilar (pillar content) yang sangat panjang dan mendalam."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=120) # Timeout lebih lama untuk konten panjang
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"[ERROR] Gagal generate: {e}")
        return "Gagal menghasilkan konten."

def fetch_unsplash_image(topic):
    query = topic.split(":")[0]
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            img_url = data["urls"]["regular"]
            filename = f"img_{random.randint(1000, 9999)}.jpg"
            img_data = requests.get(img_url).content
            with open(os.path.join(IMAGES_DIR, filename), "wb") as f:
                f.write(img_data)
            return filename
    except:
        return ""

def save_article(title, content, image_file):
    # CSS DARK MODE PRO
    css = """
    body { font-family: 'Inter', -apple-system, sans-serif; max-width: 850px; margin: auto; padding: 50px 20px; line-height: 1.8; background-color: #0f172a; color: #cbd5e1; }
    .container { background: #1e293b; padding: 40px; border-radius: 20px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }
    h1 { color: #38bdf8; font-size: 2.8em; line-height: 1.2; margin-bottom: 20px; }
    h2 { color: #f1f5f9; border-left: 5px solid #38bdf8; padding-left: 15px; margin-top: 40px; }
    h3 { color: #94a3b8; margin-top: 30px; }
    img { width: 100%; border-radius: 15px; margin: 30px 0; border: 1px solid #334155; }
    p { margin-bottom: 20px; font-size: 1.15em; color: #94a3b8; }
    strong { color: #f8fafc; }
    .back-btn { display: inline-block; margin-bottom: 30px; color: #38bdf8; text-decoration: none; font-weight: 600; }
    .back-btn:hover { color: #7dd3fc; }
    footer { text-align: center; margin-top: 50px; color: #64748b; font-size: 0.9em; border-top: 1px solid #334155; padding-top: 20px; }
    """
    
    safe_title = "".join([c for c in title.replace(" ", "_") if c.isalnum() or c == "_"])
    filename = os.path.join(ARTICLES_DIR, f"{safe_title}_{random.randint(1000, 9999)}.html")
    
    html = f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <a href="index.html" class="back-btn">← Kembali ke Beranda</a>
            <h1>{title}</h1>
            {"<img src='../images/" + image_file + "'>" if image_file else ""}
            <div class="content">{content}</div>
            <footer>Dibuat secara otomatis oleh AI Smart Blog - {datetime.now().strftime('%Y')}</footer>
        </div>
    </body>
    </html>
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

def generate_index():
    files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html") and f != "index.html"]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(ARTICLES_DIR, x)), reverse=True)
    
    css_index = """
    body { font-family: sans-serif; background: #0f172a; color: #f1f5f9; padding: 50px; text-align: center; }
    ul { list-style: none; padding: 0; max-width: 600px; margin: auto; text-align: left; }
    li { background: #1e293b; margin: 10px 0; padding: 15px; border-radius: 10px; transition: 0.3s; }
    li:hover { transform: scale(1.02); background: #334155; }
    a { color: #38bdf8; text-decoration: none; font-size: 1.2em; font-weight: bold; }
    """
    
    html = f"<html><head><style>{css_index}</style></head><body>"
    html += "<h1>🚀 Portal Artikel Masa Depan</h1><ul>"
    for file in files:
        title = file.replace("_", " ").split(".html")[0]
        html += f'<li><a href="{file}">{title}</a></li>'
    html += "</ul></body></html>"
    
    with open(os.path.join(ARTICLES_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def commit_push_github():
    print("[PROCESS] Mengirim update ke GitHub...")
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Publish Artikel Baru {datetime.now()}"])
    subprocess.run(["git", "push", "origin", GIT_BRANCH])

if __name__ == "__main__":
    # AI memikirkan 1 topik sangat mendalam setiap sesi
    title = get_ai_topic()
    content = generate_article(title)
    image_file = fetch_unsplash_image(title)
    save_article(title, content, image_file)
    
    generate_index()
    commit_push_github()
    print("[SUCCESS] Artikel Berhasil Terbit dengan Tampilan Baru!")
