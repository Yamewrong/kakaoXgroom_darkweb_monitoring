import pandas as pd
import requests

def load_bin_data(file_path):
    """BIN 데이터셋 가져오기"""
    df = pd.read_csv(file_path, dtype={'bin': str}) #문자열로 변환
    return df

def fetch_bin_info_online(bin_number):
    """데이터 셋에서 bin없을 경우 다른 사이트에서 검색"""
    url = f"https://lookup.binlist.net/{bin_number}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            country = data.get("country", {}).get("name", "Unknown Country")
            bank = data.get("bank", {}).get("name", "Unknown Bank")
            return f"카드 발행사: {country}, 은행: {bank}"
        else:
            return "확인 할 수 없는 Bin."
    except requests.RequestException:
        return "사이트 연결 에러."

def get_card_info(bin_number, df):
    """데이터셋 기반, 카드의 처음 6자리로 나라 검색, 한국이면 은행도 출력"""
    bin_prefix = str(bin_number)[:6]  #6자리만 남김
    result = df[df['bin'] == bin_prefix]
    
    if not result.empty:
        country = result.iloc[0]['country']
        bank = result.iloc[0]['issuer'] if 'issuer' in result.columns and pd.notna(result.iloc[0]['issuer']) else "Unknown Bank"
        return f"카드 발행사: {country}, 은행: {bank}"
    else:
        return fetch_bin_info_online(bin_prefix)

# 데이터셋 파일경로 입력
file_path = "/content/drive/MyDrive/Colab Notebooks/binlist-data.csv"# 데이터셋 파일경로 입력
bin_df = load_bin_data(file_path)

# 실행 부분
card_number = input("카드의 처음 6자리를 입력하세요: ")
info = get_card_info(card_number, bin_df)
print(info)
