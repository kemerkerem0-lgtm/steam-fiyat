from flask import Flask, render_template
import requests
import time

app = Flask(__name__)

def get_steam_deals():
    try:
        # 't' parametresi Steam'in bize bayat veri göndermesini engeller (Cache Busting)
        t = int(time.time())
        # cc=tr Türkiye bölgesini, l=turkish ise Türkçe dili temsil eder
        url = f"https://store.steampowered.com/api/featuredcategories?cc=tr&l=turkish&t={t}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'tr-TR,tr;q=0.9'
        }
        
        response = requests.get(url, headers=headers, timeout=10).json()
        
        # Steam'in 'Specials' (İndirimler) listesini yakalıyoruz
        specials = response.get('specials', {}).get('items', [])
        
        oyunlar = []
        for game in specials:
            # Fiyat verilerini alıyoruz
            raw_old = game.get('original_price', 0)
            raw_new = game.get('final_price', 0)
            
            # Eğer oyunun fiyat bilgisi varsa listeye ekle
            if raw_new > 0:
                # Steam API fiyatları 100 ile çarpılmış gönderir (Örn: 1000 = 10.00 TL/USD)
                # Not: Steam TR'de USD'ye geçtiği için bunlar şu an USD görünebilir
                oyunlar.append({
                    "ad": game['name'],
                    "indirim": game.get('discount_percent', 0),
                    "eski_fiyat": f"{raw_old/100:.2f}" if raw_old > 0 else "",
                    "yeni_fiyat": f"{raw_new/100:.2f}",
                    "resim": game.get('header_image'),
                    "link": f"https://store.steampowered.com/app/{game['id']}"
                })
        
        # En azından boş dönmesin diye kontrol
        return oyunlar if oyunlar else []
        
    except Exception as e:
        print(f"Veri çekilirken hata oluştu: {e}")
        return []

@app.route("/")
def index():
    # Fonksiyonu çağırıp gerçek verileri listeye aktarır
    firsatlar = get_steam_deals()
    return render_template("index.html", firsatlar=firsatlar)

if __name__ == "__main__":
    # Uygulamayı başlat
    app.run(debug=True)