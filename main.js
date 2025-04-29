'use strict';

// フォーム要素を取得
const form = document.querySelector('form');

form.addEventListener('submit', function(e) {
  e.preventDefault(); // ページリロードを防ぐ

  const name = document.getElementById('name').value || "京産太郎";
  const studentNumber = document.getElementById('studentNumber').value || "123456";
  const tittle = document.getElementById('soturontittle').value || "卒業論文のタイトル";
  const teacherName = document.getElementById('teacherName').value || "奥田次郎";
  const githubUrl = document.getElementById('githubUrl').value || "https://github.co.jp/";

  //latex,build,bibファイル用のテンプレートを生成
  //Buildファイルのテンプレート
  let latexBuild =`
    #!/bin/bash
    set -e  # エラーが出たら即終了

    # 変数
    TEX_FILE="soturon.tex"  # ここにビルドしたいtexファイル名を入れる

    # コンパイル
    lualatex "$TEX_FILE"
    bibtex "\${TEX_FILE%.tex}"  # bibtexの引数にtexファイル名を渡す
    lualatex "$TEX_FILE"
    lualatex "$TEX_FILE"

    # 画面に表示する
    echo "PDFビルド完了!" 
  `;

  

    //latexファイルのテンプレート
    let latexTemplate = `
    \\documentclass[a4paper,12pt]{article}
    \\usepackage{luatexja} % 日本語対応
    \\usepackage{graphicx} % 画像挿入用
    \\usepackage{amsmath}  % 数式用
    \\usepackage{hyperref} % リンク用
    \\usepackage{geometry} % ページ設定
    \\geometry{top=25mm, bottom=25mm, left=30mm, right=30mm}
    
    \\title{${tittle}}
    \\author{${name} \\\\ 学籍番号: ${studentNumber} \\\\ 指導教員: ${teacherName}}
    \\date{\\today}
    
    \\begin{document}
    
    \\maketitle
    
    \\begin{abstract}
    本研究では、〇〇についての研究を行い、その結果を報告する。本論文では、研究の背景、目的、方法、結果、考察、結論を述べる。
    \\end{abstract}
    
    \\tableofcontents % 目次を自動生成
    \\newpage
    
    \\section{はじめに}
    本研究の背景と目的について述べる。
    
    \\section{関連研究}
    過去の研究を紹介し、本研究との違いを明確にする。
    
    \\section{研究方法}
    どのような手法でデータを取得・分析したかを説明する。
    
    \\section{結果}
    得られた実験結果や分析結果を示す。
    
    \\section{考察}
    結果をもとに、仮説の検証や問題点について考察する。
    
    \\section{結論}
    本研究のまとめと、今後の課題について述べる。
    
    \\section*{謝辞}
    本研究を進めるにあたり、多大なるご指導をいただいた〇〇教授に深く感謝申し上げます。また、研究に協力していただいた皆様に感謝いたします。
    
    \\begin{thebibliography}{99}
    \\bibitem{sample1} 山田太郎, 「〇〇に関する研究」, 日本〇〇学会誌, 2020.
    \\bibitem{sample2} John Doe, \\textit{Research on Something}, Journal of Something, 2019.
    \\bibitem{sample3} 田中一郎, 「AI技術の進化」, 技術評論社, 2021.
    \\end{thebibliography}
    
    \\end{document}
    `.trim(); //最初と最後の空白を消す

    // 入力の要素を取得

  // コンソールに表示
  console.log(tittle);
  console.log(name);
  console.log(studentNumber);
  console.log(teacherName);
  console.log(githubUrl);

  //latexファイルの生成
  //空のzipファイルオブジェクトを生成
  const zip = new JSZip();
  
  //zipファイルにディレクトリ作成
  const folder = zip.folder("soturon");

  // zipにファイルを追加する、file(ファイル名、中身)
  folder.file(`soturon.tex`, latexTemplate);
  folder.file(`build.sh`, latexBuild);
  folder.file("説明書.txt", "これは説明書です");

  //zipを生成する
  //zipファイル生成を非同期で行う、blobはブラウザで保存できるファイル
  zip.generateAsync({ type: "blob" })
  //非同期処理の後に実行(今回はzipファイル生成後)、contentにはzipファイルが入る
    .then(function(content) {
      // ブラウザでダウンロードできるようにする
      const link = document.createElement('a');
      link.href = URL.createObjectURL(content);
      link.download = `soturon.zip`; // ダウンロードファイル名
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    });
});