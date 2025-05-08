import datetime
from PIL.ExifTags import TAGS


def get_exif_data(image):
    """画像からExifデータを取得する関数"""
    exif_data = {}

    try:
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value
    except AttributeError:
        # _getexif メソッドがない場合は空の辞書を返す
        pass
    except Exception as e:
        print(f"Exifデータ取得中のエラー: {e}")

    return exif_data


def format_date_time(date_time_str):
    """日付と時間のフォーマットを整える関数"""
    if date_time_str:
        dt = datetime.datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
        return dt.strftime("%Y/%m/%d %H:%M:%S")
    return "Unknown"


def get_specific_exif_data(exif_data):
    """指定されたExifデータのみを抽出して配列として返す関数"""
    specific_fields = [
        "Make",
        "Model",
        "LensModel",
        "FocalLength",
        "FocalLengthIn35mmFilm",
        "FNumber",
        "ApertureValue",
        "ISOSpeedRatings",
        "ExposureTime",
    ]

    result = []
    for field in specific_fields:
        value = exif_data.get(field, "Unknown")
        # 特定のフィールドの値を見やすい形式に変換
        if field == "FocalLength" and value != "Unknown":
            value = f"{int(value)}mm"
        elif field == "FNumber" and value != "Unknown":
            value = f"f/{float(value):.1f}"
        elif field == "ExposureTime" and value != "Unknown":
            if value < 1:
                value = f"1/{int(1/value)}s"
            else:
                value = f"{value}s"
        elif field == "ApertureValue" and value != "Unknown":
            value = f"{float(value):.2f}"
        elif field == "DateTimeOriginal" and value != "Unknown":
            value = format_date_time(value)

        result.append((field, value))

    return result


def print_exif_data(exif_data, specific_only=False):
    """ExifデータをターミナルにJSON形式で出力する関数"""
    print("\nExif データ:")
    print("=" * 40)
    if not exif_data:
        print("Exifデータが見つかりませんでした。")
        return

    if specific_only:
        specific_data = get_specific_exif_data(exif_data)
        print("指定されたExifデータ:")
        for key, value in specific_data:
            print(f"{key}: {value}")

        # 配列形式で表示
        print("\n配列形式:")
        print([value for _, value in specific_data])
    else:
        for key, value in sorted(exif_data.items()):
            # 表示に適した形に変換
            if key == "DateTimeOriginal" and value:
                value = format_date_time(value)
            elif key == "FocalLength" and value:
                value = f"{int(value)}mm"
            elif key == "FNumber" and value:
                value = f"f/{float(value):.1f}"
            elif key == "ExposureTime" and value:
                if value < 1:
                    value = f"1/{int(1/value)}s"
                else:
                    value = f"{value}s"

            print(f"{key}: {value}")
    print("=" * 40)
