#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import platform

# 色付き出力
class Color:
    INFO = '\033[34m'
    SUCCESS = '\033[32m'
    ERROR = '\033[31m'
    END = '\033[0m'

def print_info(msg):
    print(f"{Color.INFO}[INFO]{Color.END} {msg}")

def print_success(msg):
    print(f"{Color.SUCCESS}[SUCCESS]{Color.END} {msg}")

def print_error(msg):
    print(f"{Color.ERROR}[ERROR]{Color.END} {msg}")

def check_command(cmd):
    return shutil.which(cmd) is not None

def get_github_token():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print_error('GITHUB_TOKEN環境変数が設定されていません')
        print_info('Personal Access Tokenを作成し、GITHUB_TOKENに設定してください')
        sys.exit(1)
    return token

def create_github_repo(repo_name, description, private):
    if not shutil.which('gh'):
        print_error('GitHub CLI (gh) がインストールされていません')
        sys.exit(1)
    # gh auth status でログイン確認
    result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
    if result.returncode != 0:
        print_error('GitHub CLIで認証されていません。gh auth loginでログインしてください')
        print(result.stdout)
        sys.exit(1)
    # コマンド組み立て
    cmd = ['gh', 'repo', 'create', repo_name, '--confirm']
    if description:
        cmd += ['--description', description]
    if private:
        cmd += ['--private']
    else:
        cmd += ['--public']
    # 実行
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print_success(f"リポジトリ '{repo_name}' が正常に作成されました")
        # gh repo view でURLとユーザー名取得
        info = subprocess.run(['gh', 'repo', 'view', repo_name, '--json', 'url,owner'], capture_output=True, text=True)
        if info.returncode == 0:
            import json
            data = json.loads(info.stdout)
            clone_url = data['url'] + '.git' if not data['url'].endswith('.git') else data['url']
            username = data['owner']['login'] if isinstance(data['owner'], dict) else data['owner']
            return clone_url, username
        else:
            print_error('リポジトリ情報の取得に失敗しました')
            sys.exit(1)
    elif 'already exists' in result.stderr:
        print_error(f"リポジトリ '{repo_name}' は既に存在します")
        sys.exit(1)
    else:
        print_error(f"リポジトリの作成に失敗しました: {result.stderr}")
        sys.exit(1)

def ghq_get(clone_url):
    if check_command('ghq'):
        print_info('ghq getでリポジトリをクローン中...')
        result = subprocess.run(['ghq', 'get', clone_url])
        if result.returncode == 0:
            print_success('リポジトリが正常にクローンされました')
        else:
            print_error('リポジトリのクローンに失敗しました')
            sys.exit(1)
    elif check_command('git'):
        print_info('ghqが無いためgit cloneでクローンします')
        result = subprocess.run(['git', 'clone', clone_url])
        if result.returncode == 0:
            print_success('リポジトリが正常にクローンされました')
        else:
            print_error('リポジトリのクローンに失敗しました')
            sys.exit(1)
    else:
        print_error('ghqもgitも見つかりません')
        sys.exit(1)

def detect_shell():
    shell = os.environ.get('SHELL', '')
    comspec = os.environ.get('COMSPEC', '')
    pwsh = os.environ.get('PSModulePath', '')
    if shell:
        if 'bash' in shell or 'zsh' in shell or 'sh' in shell:
            return 'sh'
    if comspec:
        if 'cmd.exe' in comspec.lower():
            return 'cmd'
    if pwsh:
        return 'powershell'
    if os.name == 'nt':
        return 'cmd'
    return 'sh'

def print_cd_command(repo_path, shell_type):
    if shell_type == 'sh':
        print_info(f'リポジトリに移動するには: cd "{repo_path}"')
    elif shell_type == 'cmd':
        print_info(f'リポジトリに移動するには: cd /d "{repo_path}"')
    elif shell_type == 'powershell':
        print_info(f'リポジトリに移動するには: Set-Location "{repo_path}"')
    else:
        print_info(f'リポジトリに移動するには: cd "{repo_path}"')

def main():
    import argparse
    parser = argparse.ArgumentParser(description='GitHubで新規リポジトリを作成しghq get相当のクローンを行う')
    parser.add_argument('repo_name', help='リポジトリ名')
    parser.add_argument('description', nargs='?', default='', help='リポジトリの説明')
    parser.add_argument('--private', action='store_true', help='プライベートリポジトリとして作成')
    parser.add_argument('--cd', action='store_true', help='クローンしたリポジトリのディレクトリに移動するコマンドを表示')
    parser.add_argument('--cd-auto', action='store_true', help='スクリプト内でカレントディレクトリを移動（sh系のみ/サブプロセスでのみ有効）')
    args = parser.parse_args()

    # 必要なツールの存在確認
    if not check_command('curl') and not check_command('requests'):
        print_error('requestsモジュールが必要です。pip install requests でインストールしてください')
        sys.exit(1)

    print_info(f'リポジトリ名: {args.repo_name}')
    if args.description:
        print_info(f'説明: {args.description}')
    if args.private:
        print_info('プライベートリポジトリとして作成します')

    clone_url, username = create_github_repo(args.repo_name, args.description, args.private)
    ghq_get(clone_url)

    # ghq root からローカルパスを取得
    repo_path = None
    if check_command('ghq'):
        try:
            ghq_root = subprocess.check_output(['ghq', 'root'], text=True).strip()
            repo_path = os.path.join(ghq_root, f'github.com/{username}/{args.repo_name}')
        except Exception:
            repo_path = None
    elif os.path.isdir(args.repo_name):
        repo_path = os.path.abspath(args.repo_name)

    print_success('完了しました！')
    print_info(f'リポジトリURL: https://github.com/{username}/{args.repo_name}')

    if args.cd or args.cd_auto:
        shell_type = detect_shell()
        if repo_path and os.path.isdir(repo_path):
            if args.cd:
                print_cd_command(repo_path, shell_type)
            if args.cd_auto and shell_type == 'sh':
                try:
                    os.chdir(repo_path)
                    print_success(f'カレントディレクトリを {repo_path} に移動しました（このプロセス内のみ有効）')
                except Exception as e:
                    print_error(f'cdに失敗: {e}')
        else:
            print_error('ローカルリポジトリのパスが特定できませんでした')

if __name__ == '__main__':
    main() 