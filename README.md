# Video Compressor Service
## 概要

動画処理を行うプログラムです。クライアントが処理対象の動画ファイルと動画処理の内容を指定し、サーバー側でファイルを受け取り処理してからクライアントに返します。

## インストール

1. Python 3.x をインストールします。
2. `ffmpeg-python` パッケージをインストールします。
   pip install ffmpeg-python

## 使い方

### サーバーの起動

1. `server.py` を実行してサーバーを起動します。

   python3 server.py

### クライアントの起動

1. `client.py` を実行してクライアントとして動作させます。

   python3 client.py

2. 処理したい動画ファイルのパスと、処理内容の番号を入力します。

   - ★機能一覧
   - 1: 動画の圧縮
   - 2: 動画の解像度の変更
   - 3: 動画のアスペクト比の変更
   - 4: 動画を音声に変換
   - 5: GIF への変換
    

3. サーバーで動画が処理され、クライアントにダウンロードされます。
