import openai
import requests
import random
import os
import time

# ================== CONFIG ==================
openai.api_key = "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"        # Ganti dengan API OpenAI
UNSPLASH_ACCESS_KEY = "3PueUqTNwpdmuR2Z7wBesoRn6Gn2lJ9-iA9-dMP26t0"  # Ganti dengan API Unsplash
output_folder = "premium_blog_articles"
num_articles = 60  # 2 artikel per hari x 30 hari
delay_seconds = 5  # Delay antara request ke OpenAI (hindari limit)
# ============================================

# List topik variatif untuk human-like content
topics = [
    "Menghasilkan uang dari HP tanpa modal",
    "Tips diet sehat di rumah",
    "Review HP terbaru 2026",
    "Cara menabung crypto untuk pemula",
    "Travel budget murah di Indonesia",
    "Konten kreatif dan short video",
    "Freelance ringan dan microtask",
    "Reseller produk digital dan fisik",
    "Game penghasil uang legal",
    "Tips produktivitas digital di 2026",
    "Cara memulai bisnis online dari HP",
    "Tutorial editing video pendek",
    "Tips meningkatkan penghasilan pasif",
    "Teknologi AI terbaru untuk kreator",
    "Strategi konten viral di media sosial"
]

# ================== FUNCTION ==================
def generate_article(topic):
    prompt = f"""
    Buat artikel panjang 1600–2100 kata tentang: "{topic}".
    Artikel harus:
    - Human-like, natural, mudah dibaca
    - SEO-friendly & SOG ready
    - Judul unik
    - Meta description (maks 160 karakter)
    - H2/H3 untuk tiap tips atau point
    - Call-to-action di akhir
    - Bahasa Indonesia
    Output format:
    Judul:
    Meta Description:
    Artikel HTML siap copy-paste ke Blogspot
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-5-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.85,
        max_tokens=3200
    )
    
    return response['choices'][0]['message']['content']

def get_unsplash_image(query):
    """Ambil link gambar Unsplash random sesuai query"""
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
    try:
        response = requests.get(url).json()
        return response['urls']['regular']
    except:
        # fallback jika gagal
        return f"https://source.unsplash.com/800x600/?{query.replace(' ', '-')}"
# ==============================================

# Buat folder output jika belum ada
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Generate multi-artikel
for i in range(1, num_articles+1):
    topic_choice = random.choice(topics)
    print(f"Generating article {i}/{num_articles} -> Topic: {topic_choice}")
    
    # Generate artikel dari OpenAI
    article_content = generate_article(topic_choice)
    
    # Ambil gambar Unsplash header
    image_url = get_unsplash_image(topic_choice)
    
    # Buat HTML siap Blogspot
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>{topic_choice}</title>
    <meta name="description" content="{topic_choice}">
    <style>
    body {{font-family: Arial, sans-serif; line-height: 1.7; padding: 20px; color:#333;}}
    h1, h2, h3 {{color: #1a73e8;}}
    img {{width: 100%; height: auto; margin: 20px 0;}}
    </style>
    </head>
    <body>

    <h1>{topic_choice}</h1>

    <img src="{image_url}" alt="{topic_choice}">

    {article_content}

    </body>
    </html>
    """
    
    # Simpan file HTML
    file_name = f"{output_folder}/article_{i}.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"Article {i} saved: {file_name}\n")
    
    # Delay untuk menghindari rate limit
    time.sleep(delay_seconds)

print("✅ Semua artikel premium berhasil dibuat!")
print(f"Folder output: {output_folder}")
