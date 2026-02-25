import os

ARTICLES_DIR = "articles"
INDEX_FILE = os.path.join(ARTICLES_DIR, "index.html")

# Ambil semua file HTML kecuali index.html
files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html") and f != "index.html"]
files.sort(reverse=True)  # terbaru di atas

# Mulai bikin index.html
html = "<html>\n<head>\n<title>Daftar Artikel Terbaru</title>\n</head>\n<body>\n"
html += "<h1>Daftar Artikel Terbaru</h1>\n<ul>\n"

for file in files:
    title = file.replace("_", " ").replace(".html", "")
    html += f'<li><a href="{file}">{title}</a></li>\n'

html += "</ul>\n</body>\n</html>"

# Simpan
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[SUCCESS] Index dibuat di {INDEX_FILE}")
