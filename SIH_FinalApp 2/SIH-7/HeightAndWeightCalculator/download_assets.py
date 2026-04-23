import os
import requests
import logging

def download_missing_assets():
    """Download missing images from GitHub to satisfy Hugging Face binary restrictions"""
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com/SomeswararaoTellakula/DeepFit/main/SIH_FinalApp%202/SIH-7/HeightAndWeightCalculator/static/images"
    
    ASSETS = [
        "background.png",
        "image.png",
        "image1.png",
        "image2.png",
        "image3.png",
        "logo_sai.jpg",
        "hero-bg.png"
    ]
    
    # Get current directory (where app.py is)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, "static", "images")
    
    os.makedirs(target_dir, exist_ok=True)
    
    for asset in ASSETS:
        target_path = os.path.join(target_dir, asset)
        if not os.path.exists(target_path) or os.path.getsize(target_path) == 0:
            print(f"Downloading {asset} from GitHub...")
            url = f"{GITHUB_RAW_BASE}/{asset}"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(target_path, "wb") as f:
                        f.write(response.content)
                    print(f"Successfully downloaded {asset}")
                else:
                    print(f"Failed to download {asset}: Status {response.status_code}")
            except Exception as e:
                print(f"Error downloading {asset}: {e}")

if __name__ == "__main__":
    download_missing_assets()
