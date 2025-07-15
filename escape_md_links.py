#!/usr/bin/env python3
import os
import re
import sys

# マークダウンリンクの正規表現: [テキスト](URL)
MD_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]*)\)')

# 未エスケープの#のみをエスケープする正規表現
UNESCAPED_HASH_PATTERN = re.compile(r'(?<!\\)#')

def escape_hash_in_linktext(text):
    # [テキスト#foo#bar](url) → [テキスト\#foo\#bar](url)
    def replacer(match):
        linktext = match.group(1)
        url = match.group(2)
        # 既にエスケープされていない#のみを\#に置換
        escaped = UNESCAPED_HASH_PATTERN.sub(r'\\#', linktext)
        return f'[{escaped}]({url})'
    return MD_LINK_PATTERN.sub(replacer, text)

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # バイナリや非UTF-8はスキップ
        return False
    new_content = escape_hash_in_linktext(content)
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'変換: {filepath}')
        return True
    return False

def is_text_file(filename):
    # 拡張子で判定（.md, .txt, .rst, .markdown, .text など）
    return any(filename.lower().endswith(ext) for ext in ['.md', '.txt', '.rst', '.markdown', '.text'])

def main():
    import argparse
    parser = argparse.ArgumentParser(description='指定フォルダ内のテキストファイルのマークダウンリンクテキスト中の#を自動エスケープ（既にエスケープ済みはスキップ、複数#対応）')
    parser.add_argument('target_dir', help='検索対象のディレクトリ')
    args = parser.parse_args()

    changed = 0
    for root, dirs, files in os.walk(args.target_dir):
        for file in files:
            if is_text_file(file):
                path = os.path.join(root, file)
                if process_file(path):
                    changed += 1
    print(f'処理完了: {changed}ファイルを変換しました')

if __name__ == '__main__':
    main() 