#!/usr/bin/env python3
import re
import sys
import os

def convert_tags_bracket_to_list(yaml_text):
    def replacer(match):
        tags_str = match.group(1)
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        if not tags:
            return 'tags: []'
        list_str = '\n' + '\n'.join(f'  - {t}' for t in tags)  # 2スペースインデント
        return f'tags:{list_str}'
    return re.sub(r'^tags:\s*\[([^\]]*)\]\s*$', replacer, yaml_text, flags=re.MULTILINE)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.match(r'(?s)^---\n(.*?)\n---(.*)', content)
    if not m:
        return False
    yaml_part, rest = m.group(1), m.group(2)
    new_yaml = convert_tags_bracket_to_list(yaml_part)
    if new_yaml != yaml_part:
        new_content = f'---\n{new_yaml}\n---{rest}'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'変換: {filepath}')
        return True
    return False

def is_text_file(filename):
    return any(filename.lower().endswith(ext) for ext in ['.md', '.markdown', '.txt', '.rst', '.text'])

def process_dir(target_dir):
    changed = 0
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if is_text_file(file):
                path = os.path.join(root, file)
                try:
                    if process_file(path):
                        changed += 1
                except Exception as e:
                    print(f'エラー: {path}: {e}')
    print(f'処理完了: {changed}ファイルを変換しました')

def main():
    import argparse
    parser = argparse.ArgumentParser(description='YAML front matterのtagsがブラケットの場合にリストに置換（ディレクトリ再帰対応、2スペースインデント）')
    parser.add_argument('target', help='対象のファイルまたはディレクトリ')
    args = parser.parse_args()
    if os.path.isdir(args.target):
        process_dir(args.target)
    else:
        process_file(args.target)

if __name__ == '__main__':
    main() 