# ASFromPubMed
Article scraper from PubMed

🧭 開發流程與問題總結
✅ 1. 初始版本：使用 Biopython + requests 嘗試下載 PDF
利用 Entrez 搜尋關鍵詞取得 PMID。

透過 elink 將 PMID 轉成 PMC ID。

嘗試用 requests.get() 直接下載 PDF（假設網址如 .../PMCxxxx/pdf/）。

📌 問題：

有些網址如 https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11009634/pdf/ 看起來是 PDF，但實際只是個跳轉頁面或 viewer。

直接下載的結果常常是 HTML 頁面、404 錯誤或空白 PDF。

✅ 2. 嘗試補救：進一步爬取 PDF 真實網址
使用 BeautifulSoup 抓取 <a href="/pdf/xxx.pdf"> 真正 PDF 連結。

改用 pmc.ncbi.nlm.nih.gov 主機，避開跳轉問題。

📌 問題：

某些頁面載入的 PDF 是用 JavaScript 動態插入，或使用 iframe。

requests 無法取得這些非靜態內容。

✅ 3. 改用 Selenium：模擬人類打開 PDF 再列印成 PDF 檔
使用 Selenium + Chrome + CDP（Page.printToPDF）將頁面列印為 PDF。

可處理 iframe/viewer 類型 PDF。

📌 新問題與後果：

雖可列印頁面，但若原網址本質是 viewer（不是 PDF 檔本體），列印結果常為「空白」或只含介面。

更慢、更耗資源，增加依賴項（需 ChromeDriver）。

無法保證抓到的是純 PDF 內容，而是視覺畫面（有時甚至會缺圖或樣式異常）。

✅ 4. 最終穩定版：回歸使用 requests 直接抓真 PDF 檔
結合：

Biopython 抓 PMID → PMC ID。

requests + BeautifulSoup 抓 <a href="...pdf">。

檢查 Content-Type 是否為 application/pdf。

將 Selenium 完全移除。

📌 成果：

成功過濾非開放存取文章。

避免下載假 PDF 或空白檔。

效率更高、程式更輕量、依賴少。

🔍 為何一開始選擇 Selenium？
原因	說明
有些 PDF 網址實為 viewer	網頁中顯示 PDF，但實際為 iframe，無法用 requests 抓出來。
嘗試用瀏覽器模擬列印	想要透過 CDP 的 printToPDF 把頁面畫面列印成實體 PDF。
期望更穩定處理 HTML viewer	Selenium 可處理 JavaScript、iframe 等 requests 無法處理的情況。

🧨 為何後來又捨棄 Selenium？
問題	說明
🕳️ PDF 是 viewer，不是 PDF 檔	列印結果常是空白頁或 HTML 界面，不是真正 PDF 內容。
🐢 效能低下	每篇要開啟一個無頭瀏覽器，速度慢。
🧩 易錯依賴	ChromeDriver 版本相容性、安裝問題、平台不一致。
🔄 不穩定	視畫面結構可能成功，也可能失敗。

🔚 結論與建議
✅ 最終版本透過 正確解析 PMC 網頁中的 PDF 連結 + requests 檢查檔案類型，是目前最穩定、準確的方案。

❌ 不建議使用 Selenium 下載 PDF，除非內容是需要登入/動態生成頁面。

✅ 加入 open access[filter] 可預先避免抓到非開放取用文章，大幅提高成功率。
