import os

def return_news_config(app_const, lang):
    """
    Return the news config base on the specified language. The config include source, url and prompt of different news source.
        lang(string): "en" or "zh"
    """
    
    BASE_PATH = app_const['BASE_PATH']
    
    base = BASE_PATH or ''
    config_dir = os.path.join(base, 'config')
    news_config_path = os.path.join(config_dir, f'{lang}_news_config.json')
    
    if not os.path.exists(news_config_path):
        print(f"News config file not found at {news_config_path}.")
        raise FileNotFoundError(f"News config file not found: {news_config_path}")
    
    try:
        with open(news_config_path, 'r', encoding='utf-8') as f:
            news_config = f.read()
    except Exception as e:
        print(f"Failed to read news config file at {news_config_path}: {e}")
        raise RuntimeError(f"Failed to read news config file: {e}")
    
    print(f"Successfully retrieved news config from {news_config_path}.")
    return {"data": news_config, "message": "Successfully retrieved news config"}

if __name__ == "__main__":
    sample_lang = 'zh'
    result = return_news_config({}, sample_lang)
    print(result)