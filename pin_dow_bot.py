#pano linki kalsör adı target count değiştir
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def download_specific_board(board_url, target_count=69):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    folder_name = os.path.join(desktop_path, "13")

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    chrome_options = Options()
    # Sayfayı görmen gerekebilir, headless kapalı
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(board_url)
        print(f"Pano açıldı. {target_count} görsel taranıyor...")
        time.sleep(5)

        image_urls = []
        seen_urls = set()

        # Hedef sayıya ulaşana kadar veya sayfa bitene kadar tara
        attempt = 0
        while len(image_urls) < target_count and attempt < 20:
            # Sadece ana pano içindeki pinleri hedefle
            pins = driver.find_elements(By.CSS_SELECTOR, "[data-test-id='pin'] img")
            
            for img in pins:
                src = img.get_attribute("src")
                if src:
                    # En yüksek kalite linkine çevir
                    high_res = src.replace("236x", "originals").replace("474x", "originals").replace("736x", "originals")
                    
                    if high_res not in seen_urls:
                        seen_urls.add(high_res)
                        image_urls.append(high_res)
                        print(f"Bulundu: {len(image_urls)}/{target_count}")
                        
                        # Hedef sayıya ulaştıysak döngüden çık
                        if len(image_urls) >= target_count:
                            break
            
            if len(image_urls) >= target_count:
                break

            # Sayfayı biraz aşağı kaydır ve yeni resimlerin yüklenmesini bekle
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)
            attempt += 1

        # Sadece ilk target_count tanesini aldığımızdan emin olalım (fazla kaçtıysa keser)
        final_list = image_urls[:target_count]
        print(f"\nTarama bitti. {len(final_list)} görsel indiriliyor...")

        for index, url in enumerate(final_list):
            try:
                # Uzantıyı belirle
                ext = ".jpg"
                if ".png" in url.lower(): ext = ".png"
                
                filename = f"pin_{index+1}{ext}"
                filepath = os.path.join(folder_name, filename)
                
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"[{index+1}/{len(final_list)}] İndirildi: {filename}")
                else:
                    # Orijinal yoksa HD (736x) dene
                    fallback = url.replace("originals", "736x")
                    r = requests.get(fallback)
                    if r.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(r.content)
                        print(f"[{index+1}/{len(final_list)}] İndirildi (HD): {filename}")
            except Exception as e:
                print(f"Hata {index+1}: {e}")

    finally:
        driver.quit()
        print(f"\nİşlem tamamlandı! {len(final_list)} görsel Masaüstü'ndeki 'pin_pano' klasörüne kaydedildi.")

if __name__ == "__main__":
    target_url = "https://tr.pinterest.com/thelf_kv/boys-of-tommen-13/"
    download_specific_board(target_url, target_count=69)