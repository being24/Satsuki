# SCP-JP公式discord用Utility-bot:Satsuki

satsukiのリポジトリです．最近docker化しました．

## リポジトリの目的

~~そもそも専門が情報系でないSatsukiの製作者は公式リファレンスを読み落とし前述の通り，非効率的なソースコードを書いてしまっています．このため，これを再構成し効率の良いシステムを構築し，開発効率を高め，効率性と冗長性を確保するためにgithubを利用するものです．~~  
~~完成し次第，Satsukiにソースコードを移設します．~~  
このリポジトリを皐月のリポジトリとする!!

## 現在の状況について

2019-05-29: 現在，改修が終わっているのはデータベース更新プログラムであるAyameのみです．これは現在のSatsukiでは細かく分割しているCSVをそれぞれ1つにまとめたものです．これにより検索を実装することを容易にしました．

2019-06-22: 記事について対応しました．また，国コードを変換することが可能になりました．

2019-08-09: 現在，菖蒲の改修が進行中です．

2019-08-21:tale等の検索に着手しました．

2019-11-05: 大体できてきたのでうれしい．

2019-11-08: 完成しました．

2020-05-25: docker化の準備と大規模なリファクタリングの準備を行っています．

（バグ報告はissueかbotにお願いします）

### data

データやログを入れる場所です。docker化の際はこのファイルだけ永続化する予定です。

## その他

~~もとから試験実装の役割についていたもう一つのBot，Tachibanaの名前をこのプロジェクトに引き継がせます．Discordbotのシステム上，tokenの漏洩は絶対に避けなくてはならないためリポジトリ自体を分割することにしました．~~  
環境変数を導入することにしたので冗長性が増しました．

## ライセンス

ロゴ画像の素材はこちらからお借りしました．  
提供元：<http://scp-jp-archive.wdfiles.com/local--resized-images/foundation-universe/Internal%20department2.png/small.jpg>  
作者：Nanimono Demonai さん  

## 参考文献

<https://discordpy.readthedocs.io/ja/latest/index.html#>  
<https://qiita.com/Lazialize/items/81f1430d9cd57fbd82fb>
<https://cog-creators.github.io/discord-embed-sandbox/>

## スペシャルサンクス

デバッグに協力してくれたサーバー犬小屋の皆

## memo

```py
sudo docker run -d -v satsuki-data:/opt --env-file .env --restart=always being241/satsuki^
```
