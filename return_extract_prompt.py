import os

def return_extract_prompt(app_const):
    """
    Returns the prompt for extracting prompt content and help categorizing the news.
    """
    
    BASE_PATH = app_const['BASE_PATH']
    
    base = BASE_PATH or ''
    config_dir = os.path.join(base, 'config')
    extract_content_prompt_path = os.path.join(config_dir, f'extract_content_prompt.txt')
    
    if not os.path.exists(extract_content_prompt_path):
        print(f"Extract content prompt file not found at {extract_content_prompt_path}.")
        raise FileNotFoundError(f"Extract content prompt file not found: {extract_content_prompt_path}")
    
    try:
        with open(extract_content_prompt_path, 'r', encoding='utf-8') as f:
            news_config = f.read()
    except Exception as e:
        print(f"Failed to read extract content prompt file at {extract_content_prompt_path}: {e}")
        raise RuntimeError(f"Failed to read extract content prompt file: {e}")
    
    print(f"Successfully retrieved extract content prompt from {extract_content_prompt_path}.")
    return {"data": news_config, "message": "Successfully retrieved extract content prompt"}

if __name__ == "__main__":
    result = return_extract_prompt({})
    print(result)