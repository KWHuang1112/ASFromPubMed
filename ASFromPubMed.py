import os
import time
import requests
from Bio import Entrez
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 設定你的 Email（NCBI 要求）
Entrez.email = "your_email@example.com"

# 使用者參數
SEARCH_TERM = "frequency AND (ffrft[Filter])"  # 可改成關鍵字、PMID 或 PMC ID
MAX_RESULTS = 9999
SAVE_DIR = "pubmed_pdfs"
os.makedirs(SAVE_DIR, exist_ok=True)

def search_pubmed_ids(query, max_results=10):
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, usehistory="y")
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]

def resolve_final_pdf_url(base_url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.ncbi.nlm.nih.gov/"
    }
    try:
        response = requests.get(base_url, headers=headers, allow_redirects=True)
        final_url = response.url
        if final_url.endswith(".pdf"):
            return final_url
        else:
            print(f"  ❌ 跳轉後不是 PDF：{final_url}")
            return final_url
    except Exception as e:
        print(f"  ❌ 解析跳轉錯誤: {e}")
        return None

def fetch_pdf_url_from_pmid(pmid):
    handle = Entrez.elink(dbfrom="pubmed", db="pmc", id=pmid)
    records = Entrez.read(handle)
    handle.close()
    try:
        linkset = records[0]["LinkSetDb"]
        if linkset:
            pmcid = linkset[0]["Link"][0]["Id"]
            base_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/pdf/"
            pdf_url = resolve_final_pdf_url(base_url)
            return pdf_url, pmcid
    except Exception as e:
        print(f"  ❌ 找 PMC ID 失敗: {e}")
        return None, None
    return None, None

def download_pdf_with_browser(pdf_url, save_path):
    print(f"  🌐 使用瀏覽器模擬下載 PDF：{pdf_url}")

    download_dir = os.path.abspath(os.path.dirname(save_path))

    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "plugins.always_open_pdf_externally": True,
        "download.prompt_for_download": False,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        existing_files = set(os.listdir(download_dir))
        driver.get(pdf_url)
        time.sleep(8)  # 等待下載完成，可視網速調整

        new_files = set(os.listdir(download_dir)) - existing_files
        downloaded = [f for f in new_files if f.lower().endswith(".pdf")]
        if downloaded:
            os.rename(os.path.join(download_dir, downloaded[0]), save_path)
            print(f"  ✅ 已下載: {save_path}")
            return True
        else:
            print(f"  ❌ 未偵測到 PDF 檔案下載")
            return False
    except Exception as e:
        print(f"  ❌ Selenium 錯誤: {e}")
        return False
    finally:
        driver.quit()

def main():
    print(f"🔍 搜尋關鍵詞：{SEARCH_TERM}")
    pmid_list = search_pubmed_ids(SEARCH_TERM, MAX_RESULTS)
    print(f"🔗 找到 {len(pmid_list)} 筆論文，嘗試下載 PDF...\n")

    for pmid in pmid_list:
        print(f"➡️ 處理 PMID: {pmid}")
        pdf_url, pmcid = fetch_pdf_url_from_pmid(pmid)

        if pdf_url:
            print(f"  🔗 PDF 網址：{pdf_url}")
            filename = os.path.join(SAVE_DIR, f"PMC{pmcid}.pdf")
            success = download_pdf_with_browser(pdf_url, filename)
            if not success:
                print(f"  ⚠️ 無法成功下載 PDF（可能不是開放資源）")
        else:
            print(f"  ❌ 無法取得 PMC PDF\n")

        time.sleep(1)

    print("\n📁 所有作業完成，PDF 儲存於：", os.path.abspath(SAVE_DIR))

if __name__ == "__main__":
    main()
