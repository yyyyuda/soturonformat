#!/bin/bash
# 日本語TeXをPDFに変換するビルドスクリプト

platex -interaction=nonstopmode thesis.tex
bibtex thesis
platex -interaction=nonstopmode thesis.tex
platex -interaction=nonstopmode thesis.tex
dvipdfmx thesis.dvi