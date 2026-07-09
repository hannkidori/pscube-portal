@echo off
chcp 65001 > nul
title SLOT AI PORTAL - データ自動取り込み
echo ===================================================
echo   SLOT AI PORTAL - 全自動データインポート実行中...
echo ===================================================
echo.
cd /d "%~dp0"
python auto_import.py

echo.
echo ===================================================
echo   すべての処理が完了しました！
echo   ブラウザでトップページを開きます...
echo ===================================================
timeout /t 3 > nul
start index.html
