import os ##ファイルを操作するモジュール
import zipfile
import subprocess ##　pythonからターミナルを操作するモジュール
from flask import Flask, send_file, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTMLページを返すルートを追加
@app.route('/', methods=['GET', 'POST'])
@app.route('/')
def index():
    return render_template('index.html')  # HTMLファイルを返す

@app.route('/process-data', methods=['POST'])
def process_data():

    data = request.get_json()  # JSONデータを取得
    latexTemplate = data.get('latexTemplate')
    latexBuild = data.get('latexBuild')
    README = data.get('README')
    name = data.get('name')
    studentNumber = data.get('studentNumber')
    repo_name = "soturon"
    githubUrl = data.get('githubUrl')

    ## リポジトリ名とuploadsをパスとして結合
    repo_path = os.path.join(app.config['UPLOAD_FOLDER'], repo_name)

    # Gitリポジトリを作成
    try:
        # フォルダ作成
        ##　パスが存在しない場合は作成
        if not os.path.exists(repo_path):
            ## 中間ディレクトリも含めてディレクトリを作成
            os.makedirs(repo_path)

        # Git初期化
        ##([コマンド,引数], cwd=実行するディレクトリの相対パス)
        subprocess.run(['git', 'init'], cwd=repo_path)

        # サンプルファイルを作成（README.md）
        ## with文はファイル操作を行う,ファイルのオープンとクローズを自動で行う
        ## with open(ファイル名, '引数(mode)') as 変数
        ## 引数(mode)は、'w'は書き込みモード、'r'は読み込みモード
        with open(os.path.join(repo_path, 'README.md'), 'w') as f:
            ## ファイルに書き込み
            ## f.write：埋め込み文字列
            f.write(f"{README}")

        # 最初のコミット
        subprocess.run(['git', 'add', '.'], cwd=repo_path)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_path)

        with open(os.path.join(repo_path, f"{studentNumber}_{name}_卒業論文.tex"), 'w') as f:
            ## ファイルに書き込み
            ## f.write：埋め込み文字列
            f.write(f"{latexTemplate}")

        with open(os.path.join(repo_path, 'pdfbuild.sh'), 'w') as f:
            ## ファイルに書き込み
            ## f.write：埋め込み文字列
            f.write(f"{latexBuild}")


        # ZIPファイルの名前
        zip_filename = f"{repo_name}.zip"
        zip_filepath = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)

        ##　zipfileモジュールを使用して、リポジトリをZIP圧縮
        ## zipfile.ZipFile(ファイル名, モード, 圧縮方式)
        ## ZIP_DEFLATED：通常の圧縮方式
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            ## os.walk：指定ディレクトリのファイルとサブディレクトリを最下層まで取得
            ## 変数：curDir：現在のディレクトリ、dirs：サブディレクトリのリスト、files：ファイル
            for curDir, dirs, files in os.walk(repo_path):
                for file in files:
                    ## zipfile.ZipFile.write(): (圧縮するファイルの絶対パス、zipファイルの中での相対パス)
                    ## relpath：(絶対パス、 カレントディレクトリのパス)相対パスを取得
                    zipf.write(os.path.join(curDir, file), os.path.relpath(os.path.join(curDir, file), repo_path))
        if not os.path.exists(zip_filepath):
            return f"ZIP file not found: {zip_filepath}", 404
        # ZIPファイルをダウンロードリンクとして提供
        ## (ダウンロードする相対パス、 as_attachment=True：ブラウザでダウンロード)
        return send_file(zip_filepath, as_attachment=True)
    
    ##例外処理
    except Exception as e:
        ## エラーメッセージを文字列に変換して表示
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)