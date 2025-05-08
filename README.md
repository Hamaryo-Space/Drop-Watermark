# Exif データ付き写真フッタープログラム

このプログラムは写真の下部に Apple スタイルのフッターを追加し、その上に Exif データ（カメラモデル、焦点距離、F 値、シャッタースピード、ISO、撮影日時）を表示します。

## 必要条件

- Python 3.6 以上
- Pillow (PIL) ライブラリ

以下のコマンドで必要なライブラリをインストールできます：

```
pip install -r requirements.txt
```

または個別にインストール：

```
pip install pillow
```

## 対応ファイル形式

- 一般的な画像形式（JPEG）※その他の拡張子は未確認。

## 使用方法

1. `Apple.jpeg` と `SFPRODISPLAYBOLD.OTF` ファイルを `exif_footer.py` と同じディレクトリに配置してください。
2. 以下のコマンドを使用して写真を処理します：

```
python exif_footer.py <入力画像のパス> [出力画像のパス]
```

出力画像のパスを省略すると、元の画像名に "\_with_exif" が付与されたファイル名で保存されます。

### 追加オプション

特定の Exif データだけを表示するフッターを追加：

```
python exif_footer.py --specific-footer <入力画像のパス> [出力画像のパス]
```

Exif データのみを表示（画像処理なし）：

```
python exif_footer.py --print-exif <入力画像のパス>
```

特定の Exif データを配列形式で表示：

```
python exif_footer.py --specific-exif <入力画像のパス>
```

## 例

```
python exif_footer.py --specific-footer IMG_7560.jpeg myPhoto_with_apple_footer.jpg
```

## 注意

- 入力画像に Exif データが含まれていない場合、テキストは「Unknown」と表示されます。
- フォントサイズは画像の幅に対して相対的に計算されます。
