    #!/bin/bash
    set -e  # エラーが出たら即終了

    # 変数
    TEX_FILE="卒論.tex"  # ここにビルドしたいtexファイル名を入れる

    # コンパイル
    lualatex "$TEX_FILE"
    bibtex "${TEX_FILE%.tex}"
    lualatex "$TEX_FILE"
    lualatex "$TEX_FILE"

    #画面に表示する
    echo "PDFビルド完了!"