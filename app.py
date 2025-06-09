import os
import shutil
import zipfile
import subprocess
from flask import Flask, send_file, render_template, request
from werkzeug.utils import secure_filename
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, date
import romkan

app = Flask(__name__)

# ─── 定数設定 ───────────────────────────────
# プロジェクトルートの絶対パス
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# format ディレクトリの絶対パス
FORMAT_DIR = os.path.join(BASE_DIR, 'format')
# アップロード先の絶対パス
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOADS_DIR

# Jinja2 環境（.tex/.md テンプレート用）
env = Environment(
    loader=FileSystemLoader(FORMAT_DIR),
    autoescape=False
)

# ─── ヘルパー関数 ───────────────────────────
def get_fiscal_year(month, year):
    return year - 1 if month < 4 else year

# ─── ルート定義 ─────────────────────────────
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process-data', methods=['POST'])
def process_data():
    try:
        # フォームデータ取得
        fn_kanji = request.form.get('firstNameKanji', '')
        ln_kanji = request.form.get('lastNameKanji', '')
        fn_kana  = request.form.get('firstNameKana', '')
        ln_kana  = request.form.get('lastNameKana', '')
        title    = request.form.get('title', '')
        stu_no   = request.form.get('studentNumber', '')
        teacher  = request.form.get('teacherName', '')
        faculty  = request.form.get('faculty', '')

        now = datetime.now()
        fiscal = get_fiscal_year(date.today().month, now.year)

        # ローマ字変換
        fn_roma = romkan.to_roma(fn_kana)
        ln_roma = romkan.to_roma(ln_kana)
        repo_name = f"{fiscal}bthesis_{fn_roma}"

        # テンプレート読み込み
        tex_tmpl    = env.get_template('thesis_template.tex')
        readme_tmpl = env.get_template('README.md')

        # レンダリング
        rendered_tex    = tex_tmpl.render(
            firstName=fn_kanji,
            lastName=ln_kanji,
            title=title,
            studentNumber=stu_no,
            teacherName=teacher,
            faculty=faculty,
            year=fiscal
        )
        rendered_readme = readme_tmpl.render(
            firstNameKanji=fn_kanji,
            lastNameKanji=ln_kanji,
            firstNameRomaji=fn_roma,
            title=title,
            year=fiscal
        )

        # 作業ディレクトリ再生成
        repo_path = os.path.join(UPLOADS_DIR, repo_name)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        os.makedirs(repo_path)

        # Git 初期化
        subprocess.run(['git', 'init'], cwd=repo_path, check=True)

        # テキストファイル作成
        for fname, content in {
            'thesis.tex': rendered_tex,
            'README.md': rendered_readme
        }.items():
            with open(os.path.join(repo_path, fname), 'w', encoding='utf-8') as f:
                f.write(content)

        # images フォルダに EPS コピー
        images_dir = os.path.join(repo_path, 'images')
        os.makedirs(images_dir, exist_ok=True)
        eps_src = os.path.join(FORMAT_DIR, 'javassist.eps')
        eps_dst = os.path.join(images_dir, 'javassist.eps')
        shutil.copy2(eps_src, eps_dst)

        # その他フォーマットファイルをコピー
        for fname in [
            'csg-thesis.sty',
            'thesis.bib',
            'csg-thesis.bst',
            'latexmkrc',
            'llmk.toml'
        ]:
            src = os.path.join(FORMAT_DIR, fname)
            dst = os.path.join(repo_path, fname)
            shutil.copy2(src, dst)

        # サンプル PDF をコピー
        pdf_src = os.path.join(FORMAT_DIR, 'thesis.pdf')
        pdf_dst = os.path.join(repo_path, 'theisi.pdf')
        shutil.copy2(pdf_src, pdf_dst)


        # ZIP 作成
        zip_name = f"{repo_name}.zip"
        zip_path = os.path.join(UPLOADS_DIR, zip_name)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(repo_path):
                for fn in files:
                    full = os.path.join(root, fn)
                    arcname = os.path.relpath(full, repo_path)
                    zipf.write(full, arcname)

        # ZIP ダウンロード
        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
