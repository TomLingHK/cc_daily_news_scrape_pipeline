import os
import json


def check_added_url(app_const, input_data_list=None, date=None):
    """Return items from input_data_list whose `article_url` is NOT present in added_url_{date}.txt.

    If the target txt file is not found, return the original list.
    Output format: { 'data': [...], 'message': 'Task completed.' }
    """
    if input_data_list is None:
        print("No data list, returning...")
        return {"data": [], "message": "No input data received"}
    if date is None:
        print("No date, returning...")
        return {"data": [], "message": "No input date received"}

    BASE_PATH = app_const['BASE_PATH']
    TXT_PREFIX = app_const['ADDED_URL_TXT_PREFIX']
    
    year = date[:4]
    month = date[4:6]
    
    base = BASE_PATH or ''
    
    output_dir = os.path.join(base, 'output')
    year_dir = os.path.join(output_dir, year)
    month_dir = os.path.join(year_dir, month)
    
    if not os.path.exists(year_dir):
        return {"data": input_data_list, "message": "Target file not found; returning original list."}
    if not os.path.exists(month_dir):
        return {"data": input_data_list, "message": "Target file not found; returning original list."}
    
    added_path = os.path.join(month_dir, f'{TXT_PREFIX}{date}.txt')
    

    # If the added_url file does not exist, return original list
    if not os.path.exists(added_path):
        return {"data": input_data_list, "message": "Target file not found; returning original list."}

    seen = set()
    try:
        with open(added_path, 'r', encoding='utf-8') as f:
            for line in f:
                u = line.strip()
                if u:
                    seen.add(u)
    except Exception:
        # On read failure, be conservative and return original list
        return {"data": input_data_list, "message": "Failed to read target file; returning original list."}

    # Filter input list: keep items whose article_url is not in seen
    result = []
    for item in input_data_list:
        # item may be dict-like
        if isinstance(item, dict):
            url = item.get('article_url')
        else:
            # fallback: attempt attribute access
            url = getattr(item, 'article_url', None)

        # include if url is missing or not in seen
        if url is None or str(url) not in seen:
            result.append(item)

    print(f"Returned {len(result)} items that are not in the added_url file.")
    return {"data": result, "message": "Task completed."}


if __name__ == "__main__":
    # simple smoke test
    sample = [
  {
    "content": "政府向立法會提交網約車服務條例草案，引入網約車規管制度，建議提供服務的平台、車輛和司機三方均須領牌。當局預計首批持牌平台最快明年第四季開始營運。條例亦要求網約車車輛在每次申請許可證或續期時，車齡須低於12年。\n\n立法會交通事務委員會委員田北辰建議，網約車數量以一萬輛作為起步，因為目前市面「白牌車」數量已遠超過這個數字，若然立法後，網約車數量大減，將令市民更難「叫車」。\n\n他又認為，條例草案應該鼓勵「車盡其用」，不應該「管車又管人」，要求獲許可證的私家車，必須由車主駕駛，他擔心一旦車主放假，網約車又未能出租，在一些時段，網約車供應會大減，同時會令持牌的網約車平台加重行政工作。\n\n另一名委員陳恒鑌表示，支持政府提出的規管框架，認為由持有許可證的私家車車主，駕駛領牌的網約車，可以防止炒賣牌證。\n\n至於網約車的數量，陳恆鑌建議政府要再做研究和調查，了解市場情況，但認為在推行初期，可考慮早前坊間一些建議，以千計的數量作為起步。",
    "title": "田北辰建議網約車以一萬輛起步　陳恒鑌支持政府提出的規管框架 - RTHK",
    "date": "2025-09-04",
    "article_url": "https://news.rthk.hk/rthk/ch/component/k2/1821256-20250904.htm?archive_date=2025-09-04"
  },
  {
    "content": "香港郵政表示，與本地物流服務供應商「海迅供應鏈」原有兩份貨車租賃服務合約，合約期間一直密切監察海迅的服務表現，當發現表現轉差至未能令香港郵政信納能繼續履行合約的要求，香港郵政已採取行動終止兩份合約。香港郵政回覆查詢說，兩份合約分別為輕型貨車租賃服務，合約金額約2590萬元，原定合約期為2024年6月1日至2026年5月31日；另外5.5噸貨車租賃服務，合約金額約530萬元，原定合約期為2025年1月1日至2026年12月31日。發言人說，香港郵政根據政府相關採購規例，透過公開招標進行兩項服務採購，並按有關招標文件所載技術評分準則及投標價格，在符合車種規格及數量等指定要求的標書中揀選中標者，投標者「海迅」在技術評分及投標價格兩方面取得最高合併分數成為中標者。發言人指出，香港郵政在批出合約前，對海迅作財務審核及要求海迅提供按標書要求的車輛種類及數目予香港郵政檢驗，由於海迅就輕型貨車租賃服務合約未能通過財務審核，因此已按規定向香港郵政提供合約的金額6%的合約按金；至於5.5噸貨車租賃服務合約，海迅亦已按規定向香港郵政提供合約的金額2%的合約按金；而海迅提供的車輛種類及數目通過香港郵政檢驗，因此獲批出兩份合約。發言人說，就輕型貨車租賃服務合約，香港郵政就海迅已提供的服務共支付800萬元；至於5.5噸貨車租賃服務合約，由於海迅提供的服務一直欠佳，香港郵政並無支付任何費用，當海迅在兩份合約期間未能提供足夠車輛時，香港郵政已以其他方式補充車輛，所以郵政服務並未受影響，當中涉及的額外費用，香港郵政會在合約按金中扣除。香港郵政會就兩份合約餘下的合約期進行招標，期間會以其他方式安排車輛運輸服務。",
    "title": "香港郵政終止兩份「海迅供應鏈」貨車租賃服務合約",
    "date": "2025-09-04",
    "article_url": "https://news.rthk.hk/rthk/ch/component/k2/1821253-20250904.htm"
  }]
    print(json.dumps(check_added_url({ 'BASE_PATH': './daily_news_data/', 'ADDED_URL_TXT_PREFIX': "added_url_" }, sample, '20250904'), ensure_ascii=False, indent=2))
