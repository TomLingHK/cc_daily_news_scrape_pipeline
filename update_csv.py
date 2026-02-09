import os
import glob
import pandas as pd
from datetime import datetime
import json

def _load_added_urls(dir_path, txt_prefix):
    """Load all URLs recorded in ADDED_URL_TXT_PREFIX*.txt files in dir_path."""
    urls = set()
    pattern = os.path.join(dir_path or '.', f'{txt_prefix}*.txt')
    for p in glob.glob(pattern):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                for line in f:
                    u = line.strip()
                    if u:
                        urls.add(u)
        except Exception:
            continue
    return urls

def add_all_data(base_path, csv_template_path, input_list, txt_prefix, encoding='utf-8-sig'):
    """Append rows from input_list to a CSV file, skipping duplicates based on `article_url`.

    encoding: CSV file encoding to use when reading/writing (defaults to 'utf-8-sig').
    """
    cols = ['title', 'date', 'article_url', 'website_source', 'content']
    # cols = ['title', 'date', 'article_url', 'complaint_nature', 'complaint_category']
    # cols = ['title', 'date', 'article_url', 'category', 'strength', 'confidence']

    rows = []
    new_urls = []
    
    output_dir = os.path.join(base_path, 'output')
    
    if not os.path.exists(csv_template_path):
        raise FileNotFoundError(f"CSV file not found: {csv_template_path}")

    # Start with URLs recorded in ADDED_URL_TXT_PREFIX*.txt files
    existing_urls = _load_added_urls(output_dir, txt_prefix)

    try:
        existing_df = pd.read_csv(csv_template_path, encoding=encoding)
        if 'article_url' in existing_df.columns:
            existing_urls.update(existing_df['article_url'].dropna().astype(str).tolist())
    except Exception:
        pass
    
    def _get(i, key):
        if isinstance(i, dict):
            return i.get(key)
        return getattr(i, key, None)

    for item in input_list:
        url = _get(item, 'article_url')
        # Treat empty/None URLs as new entries (you may adjust this policy)
        if url is not None and str(url) in existing_urls:
            continue
        rows.append([
            _get(item, 'title'),
            _get(item, 'date'),
            url,
            # _get(item, 'article_url'),
            ####################################
            _get(item, 'website_source'),
            _get(item, 'content')
            ####################################
            # _get(item, 'complaint_nature'),
            # _get(item, 'complaint_category')
            ####################################
            # _get(item, 'category'),
            # _get(item, 'strength'),
            # _get(item, 'confidence'),
            ####################################
        ])
        if url is not None:
            existing_urls.add(str(url))
            new_urls.append(str(url))

    # Build DataFrame combining existing CSV (if present) and new rows.
    df_new = pd.DataFrame(rows, columns=cols) if rows else None

    if os.path.exists(csv_template_path):
        try:
            df = pd.read_csv(csv_template_path, encoding=encoding)
        except Exception:
            df = pd.DataFrame(columns=cols)

        if df_new is not None and not df_new.empty:
            df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new if df_new is not None else pd.DataFrame(columns=cols)

    return df, new_urls, df_new

def update_csv_sheet(app_const, input_data_list=None, date=None, encoding='utf-8-sig'):
    """Main entrypoint matching update_sheet.update_excel_sheet signature but for CSV.

    Parameters:
    - base_path: path prefix where `csv_template.csv` is located/should be created
    - input_data_list: list of dicts with keys `title`, `date`, `article_url`, `website_source`, `content`
    - encoding: CSV file encoding to use when reading/writing (defaults to 'utf-8-sig')
    """
    
    if input_data_list is None:
        print("No data list, returning...")
        return 'No input data received'
    if date is None:
        print("No date, returning...")
        return 'No input date received'

    BASE_PATH = app_const['BASE_PATH']
    TXT_PREFIX = app_const['ADDED_URL_TXT_PREFIX']
    CSV_PREFIX = app_const['DAILY_NEWS_CSV_PREFIX']
    
    year = date[:4]
    month = date[4:6]
    
    base = BASE_PATH or ''
    csv_template_path = os.path.join(base, 'csv_template.csv')

    # Build combined DataFrame (does not overwrite original file)
    df, new_urls, df_new = add_all_data(BASE_PATH, csv_template_path, input_data_list, TXT_PREFIX, encoding=encoding)

    
    # Create timestamped result file name
    output_dir = os.path.join(base, 'output')
    csv_name = f'{CSV_PREFIX}{date}.csv'
    year_dir = os.path.join(output_dir, year)
    month_dir = os.path.join(year_dir, month)
    csv_path = os.path.join(month_dir, csv_name)
    
    if not os.path.exists(year_dir):
        os.makedirs(year_dir, exist_ok=True)
    if not os.path.exists(month_dir):
        os.makedirs(month_dir, exist_ok=True)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # If there's a results CSV for this date already, append only the newly added rows.
    if os.path.exists(csv_path):
        if df_new is not None and not df_new.empty:
            try:
                df_new.to_csv(csv_path, index=False, encoding=encoding, header=False, mode='a')
                rows_added = len(df_new)
            except Exception:
                # Fallback: overwrite full file if append fails
                df.to_csv(csv_path, index=False, encoding=encoding)
                rows_added = len(df_new) if df_new is not None else 0
        else:
            # nothing new to append; leave file as-is
            rows_added = 0
    else:
        # No existing result file: write full dataframe (includes new rows)
        df.to_csv(csv_path, index=False, encoding=encoding)
        rows_added = len(df_new) if df_new is not None else 0

    # Write a timestamped file recording newly added URLs (if any) by appending
    added_path = os.path.join(month_dir, f'{TXT_PREFIX}{date}.txt')
    return_msg = ""
    
    if new_urls:
        try:
            with open(added_path, 'a', encoding='utf-8') as f:
                for u in new_urls:
                    f.write(u + '\n')
            print(f"✅ Appended {rows_added} new rows and wrote results to {csv_path}")
            print(f"📄 Recorded added URLs to {added_path}")
            return_msg = f"Appended {rows_added} new rows and wrote results to {csv_path}"
        except Exception:
            print(f"✅ Appended {rows_added} new rows and wrote results to {csv_path} (failed to update added_url file)")
            return_msg = f"Appended {rows_added} new rows and wrote results to {csv_path} (failed to update added_url file)"
    else:
        print(f"ℹ️ No new rows to add; results stored at {csv_path}")
        return_msg = f"No new rows to add; results stored at {csv_path}"

    return {"message": return_msg}

if __name__ == "__main__":
    sample_path = 'news_study_output.json'
    if os.path.exists(sample_path):
        with open(sample_path, 'r', encoding='utf-8') as f:
            try:
                sample = json.load(f)
            except Exception:
                sample = None
        if sample:
            update_csv_sheet('', sample)
        else:
            update_csv_sheet()
    else:
        update_csv_sheet()
