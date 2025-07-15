#!/usr/bin/env python3
import re
import sys
import os

def indent_yaml_lists(yaml_text):
    # 1. リスト項目（- item）で始まる行を検出
    # 2. 先頭がタブやスペース3個以上、またはスペース0個の場合も2スペースで正規化
    lines = yaml_text.splitlines()
    new_lines = []
    for line in lines:
        # - item の前に任意の空白（タブまたはスペース）
        m = re.match(r'^[ \t]*- ', line)
        if m:
            # 2スペース+ - item で正規化
            new_line = re.sub(r'^[ \t]*- ', '  - ', line)
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.match(r'(?s)^---\n(.*?)\n---(.*)', content)
    if not m:
        return False
    yaml_part, rest = m.group(1), m.group(2)
    new_yaml = indent_yaml_lists(yaml_part)
    if new_yaml != yaml_part:
        new_content = f'---\n{new_yaml}\n---{rest}'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'インデント修正: {filepath}')
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
    print(f'処理完了: {changed}ファイルを修正しました')

def main():
    import argparse
    parser = argparse.ArgumentParser(description='YAML front matter内のリストがインデントされていなければ2スペースでインデント（ファイル/ディレクトリ再帰対応、タブや3スペース以上も正規化）')
    parser.add_argument('target', help='対象のファイルまたはディレクトリ')
    args = parser.parse_args()
    if os.path.isdir(args.target):
        process_dir(args.target)
    else:
        process_file(args.target)

if __name__ == '__main__':
    main() 
