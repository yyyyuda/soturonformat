import os ##ファイルを操作するモジュール
import shutil ##ファイルやディレクトリを操作するモジュール
import zipfile
import subprocess ##　pythonからターミナルを操作するモジュール
from flask import Flask, send_file, render_template, request, jsonify
from werkzeug.utils import secure_filename
from jinja2 import Environment, FileSystemLoader,Template
from datetime import datetime,date # 日付と時刻を扱うモジュール
import romkan # ローマ字変換ライブラリ

app = Flask(__name__)

env = Environment(loader=FileSystemLoader('format'))

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 年度を取得する関数
def get_fiscal_year(month,year):
    if month < 4:
        year -= 1
    return year


# HTMLページを返すルートを追加
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')  # HTMLファイルを返す

@app.route('/process-data', methods=['POST'])
def process_data():

    # フォームデータの取得
    firstNameKanji = request.form.get('firstNameKanji', '')
    lastNameKanji = request.form.get('lastNameKanji', '')
    lastNameKana = request.form.get('lastNameKana', '')
    firstNameKana = request.form.get('firstNameKana', '')
    title = request.form.get('title', '')
    studentNumber = request.form.get('studentNumber', '')
    teacherName = request.form.get('teacherName', '')
    faculty = request.form.get('faculty', '')

    # 日付の取得
    year = datetime.now().year  #  年を取得
    month = date.today().month # 月を取得
    year = get_fiscal_year(month,year)  # 年度を取得

    # ローマ字変換
    firstNameRomaji = romkan.to_roma(firstNameKana)
    lastNameRomaji = romkan.to_roma(lastNameKana)
    repo_name = f"{year}bthesis_{firstNameRomaji}"

    # テンプレートの取得
    tex_template = env.get_template('thesis_template.tex')
    readme_template = env.get_template('README.md')
    build_template = env.get_template('pdf_build.sh')

    # texテンプレートに埋め込み
    rendered_tex = tex_template.render(
            firstName=firstNameKanji,
            lastName=lastNameKanji,
            title=title,
            studentNumber=studentNumber,
            teacherName=teacherName,
            faculty=faculty,
            year=year  
        )
    
    # READMEテンプレートに埋め込み
    rendered_readme = readme_template.render(
        firstNameKanji=firstNameKanji,
        lastNameKanji=lastNameKanji,
        firstNameRomaji=firstNameRomaji,
        title=title,
        year=year,
     )
    
    # buildファイルテンプレートに埋め込み
    rendered_build = build_template.render(
        repo_name=repo_name
    )

    # ファイル名と内容の辞書を作成
    files = {
    'thesis.tex': rendered_tex,
    'README.md': rendered_readme,
    'pdf_build.sh': rendered_build,
    }

    ## リポジトリ名とuploadsをパスとして結合
    repo_path = os.path.join(app.config['UPLOAD_FOLDER'], repo_name)

    # Gitリポジトリを作成
    try:
        uploads_dir = app.config['UPLOAD_FOLDER']
        # フォルダ作成
        ## パスが存在しない場合は作成
        if os.path.exists(uploads_dir):
            for item in os.listdir(uploads_dir):
                item_path = os.path.join(uploads_dir, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)  # ファイル or シンボリックリンク
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # サブディレクトリを再帰的に削除

        os.makedirs(repo_path)

        # Git初期化
        ##([コマンド,引数], cwd=実行するディレクトリの相対パス)
        subprocess.run(['git', 'init'], cwd=repo_path)

        # サンプルファイルを作成（README.md）
        ## with文はファイル操作を行う,ファイルのオープンとクローズを自動で行う
        ## with open(ファイル名, '引数(mode)') as 変数
        ## 引数(mode)は、'w'は書き込みモード、'r'は読み込みモード
        for filename, content in files.items():
            with open(os.path.join(repo_path, filename), 'w') as f:
                f.write(content)
        
        # ファイルの追加
        with open('format/csg-thesis.sty', 'r') as f: 
            sty = f.read()
        with open(os.path.join(repo_path, 'csg-thesis.sty'), 'w') as f:
            f.write(sty)

        with  open('format/thesis.bib', 'r') as f:
            bib = f.read()
        with open(os.path.join(repo_path, 'thesis.bib'), 'w') as f:
            f.write(bib)

        with open('format/javassist.eps', 'r') as f:
            eps = f.read()
        with open(os.path.join(repo_path, 'javassist.eps'), 'w') as f:
            f.write(eps)
        
        with open('format/csg-thesis.bst', 'r') as f:
            bst = f.read()
        with open(os.path.join(repo_path, 'csg-thesis.bst'), 'w') as f:
            f.write(bst)

        with open('format/latexmkrc', 'r') as f:
            latexmkrc = f.read()
        with open(os.path.join(repo_path, 'latexmkrc'), 'w') as f:
            f.write(latexmkrc)

        # 最初のコミット
        subprocess.run(['git', 'add', '.'], cwd=repo_path)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_path)


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