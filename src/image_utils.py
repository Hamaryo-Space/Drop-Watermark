from PIL import Image, ImageFont, ImageDraw, ExifTags
from PIL.ExifTags import TAGS
import piexif
from io import BytesIO

from exif_utils import get_exif_data, format_date_time


def apply_orientation(image):
    """画像の向きを適切に修正する関数"""
    try:
        # すべての画像に _getexif メソッドがあるとは限らない
        if not hasattr(image, "_getexif") or image._getexif() is None:
            return image, None

        exif = image._getexif()
        orientation_tag = next(
            (k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None
        )

        if orientation_tag and orientation_tag in exif:
            orientation = exif[orientation_tag]

            # 向きを修正する必要がある場合
            if orientation in [2, 3, 4, 5, 6, 7, 8]:
                # 新しいイメージを作成（向きを修正）
                if orientation == 2:
                    # 左右反転
                    return image.transpose(Image.FLIP_LEFT_RIGHT), exif
                elif orientation == 3:
                    # 180度回転
                    return image.transpose(Image.ROTATE_180), exif
                elif orientation == 4:
                    # 上下反転
                    return image.transpose(Image.FLIP_TOP_BOTTOM), exif
                elif orientation == 5:
                    # 左右反転して、反時計回りに90度回転
                    return (
                        image.transpose(Image.FLIP_LEFT_RIGHT).transpose(
                            Image.ROTATE_90
                        ),
                        exif,
                    )
                elif orientation == 6:
                    # 反時計回りに270度回転（≒時計回りに90度回転）
                    return image.transpose(Image.ROTATE_270), exif
                elif orientation == 7:
                    # 左右反転して、反時計回りに270度回転
                    return (
                        image.transpose(Image.FLIP_LEFT_RIGHT).transpose(
                            Image.ROTATE_270
                        ),
                        exif,
                    )
                elif orientation == 8:
                    # 反時計回りに90度回転
                    return image.transpose(Image.ROTATE_90), exif

        # 向きの修正が不要、または方向のタグがない場合は元の画像を返す
        return image, exif
    except Exception as e:
        print(f"画像の向き修正中にエラー: {e}")
        return image, None


def draw_standard_footer(draw, exif_data, img, width_ratio, font):
    """標準のフッターを描画する関数"""
    model = exif_data.get("Model", "Unknown")
    focal_length = exif_data.get("FocalLength", "")
    if focal_length:
        focal_length = f"{int(focal_length)}mm"

    f_number = exif_data.get("FNumber", "")
    if f_number:
        f_number = f"f/{float(f_number):.1f}"

    exposure_time = exif_data.get("ExposureTime", "")
    if exposure_time:
        if exposure_time < 1:
            exposure_time = f"1/{int(1/exposure_time)}s"
        else:
            exposure_time = f"{exposure_time}s"

    iso = exif_data.get("ISOSpeedRatings", "")
    if iso:
        iso = f"ISO {iso}"

    # 日付以外のテキストと日付を分けて描画するため、分割
    exif_text_without_date = (
        f"{model}  {focal_length}  {f_number}  {exposure_time}  {iso}"
    )

    # 座標を画像幅に対する比率で計算
    base_y_offset = 25 * width_ratio  # 基準位置（Y座標）
    base_left_margin = 20 * width_ratio  # 左余白

    # テキストの位置を計算（フッターの上端からの相対位置）
    text_y_position = img.height + int(base_y_offset)
    text_x_position = int(base_left_margin)

    # メインの情報を黒色で描画
    draw.text(
        (text_x_position, text_y_position),
        exif_text_without_date,
        fill=(0, 0, 0),  # 黒色
        font=font,
    )


def draw_specific_footer(
    draw, exif_data, img, width_ratio, font, camera_font, date_font
):
    """特定のExifデータを表示するフッターを描画する関数"""
    model = exif_data.get("Model", "Unknown")
    camera_make = exif_data.get("Make", "")

    focal_length_35mm = exif_data.get("FocalLengthIn35mmFilm", "")
    if focal_length_35mm:
        focal_length_35mm = f"{focal_length_35mm}mm"

    f_number = exif_data.get("FNumber", "")
    if f_number:
        f_number = f"f/{float(f_number):.1f}"

    iso = exif_data.get("ISOSpeedRatings", "")
    if iso:
        iso = f"ISO {iso}"

    exposure_time = exif_data.get("ExposureTime", "")
    if exposure_time:
        if exposure_time < 1:
            exposure_time = f"1/{int(1/exposure_time)}s"
        else:
            exposure_time = f"{exposure_time}s"

    exif_text = f"{model}"
    exif_text_camera = f"{focal_length_35mm}   {f_number}   {exposure_time}   {iso}"

    # 座標を画像幅に対する比率で計算
    base_y_offset = 110 * width_ratio  # 基準位置（Y座標）
    base_left_margin = 80 * width_ratio  # 左余白
    camera_info_x = 1900 * width_ratio  # カメラ情報のX位置
    camera_info_y_offset = 12 * width_ratio  # カメラ情報のY位置調整
    date_y_offset = 85 * width_ratio  # 日付のY位置調整

    # モデル名の位置をスケーリング
    text_y_position = img.height + int(base_y_offset)
    text_x_position = int(base_left_margin)

    # モデル名 - Appleの場合のみ表示
    if "Apple" in camera_make:
        draw.text(
            (text_x_position, text_y_position),
            exif_text,
            fill=(0, 0, 0),  # 黒色
            font=font,
        )

    # カメラ情報の位置をスケーリング
    camera_x_position = int(text_x_position + camera_info_x)
    camera_y_position = int(text_y_position - camera_info_y_offset)

    # カメラ情報
    draw.text(
        (camera_x_position, camera_y_position),
        exif_text_camera,
        fill=(0, 0, 0),  # 黒色
        font=camera_font,
    )

    date_time = format_date_time(exif_data.get("DateTimeOriginal", ""))

    # 日付の位置をスケーリング
    date_y_position = int(text_y_position + date_y_offset)

    # 日付を灰色で描画
    draw.text(
        (camera_x_position, date_y_position),
        date_time,
        fill=(159, 159, 159),  # 灰色
        font=date_font,
    )


def add_footer_with_exif(
    input_image_path,
    output_image_path,
    footer_image_path,
    font_path,
    print_only=False,
    specific_only=False,
    specific_footer=False,
):
    """写真の下部にフッターとExifデータを追加する関数"""
    try:
        # 入力画像を開く
        img = Image.open(input_image_path)

        # DPI情報を取得
        dpi = img.info.get("dpi")

        # 元の画像からExifバイトデータを取得（後で保存するため）
        original_exif_bytes = None
        if "exif" in img.info:
            original_exif_bytes = img.info["exif"]

        # 画像の向きを適切に修正し、元のExifデータを保持
        img, original_exif = apply_orientation(img)

        # 基準となる画像幅（標準幅）を定義
        standard_width = 3000.0
        # 実際の画像幅と標準幅の比率を計算
        width_ratio = img.width / standard_width

        # Exifデータを取得（回転補正前のExifデータを優先）
        if original_exif:
            # 元のExifデータから辞書を再構築
            exif_data = {}
            for tag, value in original_exif.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value
        else:
            # 回転後の画像からExifデータを取得（元のExifデータが取れない場合のフォールバック）
            exif_data = get_exif_data(img)

        # print_onlyがTrueの場合、Exifデータを表示して終了
        if print_only:
            from exif_utils import print_exif_data

            print_exif_data(exif_data, specific_only)
            return

        # フッター画像を開く
        footer = Image.open(footer_image_path)

        # フッターを入力画像の幅に合わせてリサイズ
        footer_resized = footer.resize(
            (img.width, footer.height * img.width // footer.width)
        )

        # 新しい画像を作成（元の画像 + フッター分の高さ）
        new_img = Image.new(
            "RGB", (img.width, img.height + footer_resized.height), (255, 255, 255)
        )
        new_img.paste(img, (0, 0))
        new_img.paste(footer_resized, (0, img.height))

        # フォントをロード
        font_size = int(img.width * 0.03)  # 画像幅に対する相対的なフォントサイズ
        font = ImageFont.truetype(font_path, font_size)

        # カメラ情報のフォントをロード
        camera_font_size = int(
            img.width * 0.022
        )  # 画像幅に対する相対的なフォントサイズ
        camera_font = ImageFont.truetype(font_path, camera_font_size)

        # 日付情報のフォントをロード
        date_font_size = int(img.width * 0.015)  # 画像幅に対する相対的なフォントサイズ
        date_font = ImageFont.truetype(font_path, date_font_size)

        draw = ImageDraw.Draw(new_img)

        # フッターテキストを描画
        if specific_footer:
            draw_specific_footer(
                draw, exif_data, img, width_ratio, font, camera_font, date_font
            )
        else:
            draw_standard_footer(draw, exif_data, img, width_ratio, font)

        # 新しい画像を保存（DPIとExifデータを保持）
        if original_exif_bytes:
            # 元のExifデータを使用して保存
            if dpi:
                new_img.save(output_image_path, dpi=dpi, exif=original_exif_bytes)
            else:
                new_img.save(output_image_path, exif=original_exif_bytes)
        else:
            # Exifデータがない場合はDPIだけ設定
            if dpi:
                new_img.save(output_image_path, dpi=dpi)
            else:
                new_img.save(output_image_path)

        print(f"画像が保存されました: {output_image_path}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
