# OekakiPy

Pyxelを使った複数人のリアルタイムお絵描きゲームです。
 
## DEMO
 
![oekaki_demo4](https://user-images.githubusercontent.com/28151082/108855980-eb1b3700-762c-11eb-8778-a7dd158ce798.gif)
 
## Features

途中参加の場合でもそれまでに書かれた絵の続きからお絵描きに参加できます。
絵は参加者が全員いなくなるまで保存されます。
 
## Requirement

以下の環境で動作を確認しています。

* python 3.8.6
* pyxel 1.4.3 (client only)
* Twisted 20.3.0 (server only)
 
## Installation
 
```bash
pip install pyxel
pip install twisted
```
 
## Usage

### ゲームの起動

Oekaki_server.pyを先に起動する必要があります。
 
```bash
python Oekaki_server.py
python Oekaki_client.py
```

### 設定

'setting.txt'でホストとポートを指定できます。

```text
HOSTNAME=ホスト
PORT=ポート
```

### ゲームの操作
開始したら3桁の番号を入力して部屋を決めます。

同じ部屋のユーザ同士でお絵描きを楽しむことができます。

クリック、ドラッグで描画ができます。

マウスホイールで色の変更ができます。
 
## Author
 
* sorococoa
* Twitter : @sirococoa1
 
## License
 
OekakiPy は[MIT license](https://en.wikipedia.org/wiki/MIT_License)です。
