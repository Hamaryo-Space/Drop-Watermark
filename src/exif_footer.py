import os
import sys
from image_utils import add_footer_with_exif
from PIL import Image
from exif_utils import get_exif_data


def main():
    # ヘルプ表示
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print("使用方法:")
        print(
            "  Exifデータのみ表示:   python exif_footer.py --print-exif <input_image_path>"
        )
        print(
            "  本スクリプトで使用しているExifデータを配列形式で表示: python exif_footer.py --specific-exif <input_image_path>"
        )
        print(
            "  特定のExifデータをフッターに表示: python exif_footer.py --specific-footer <input_image_path> [output_image_path]"
        )
        sys.exit(1)

    # オプションの処理
    print_only = False
    specific_only = False
    specific_footer = False

    if sys.argv[1] == "--print-exif":
        if len(sys.argv) < 3:
            print("使用方法: python exif_footer.py --print-exif <input_image_path>")
            sys.exit(1)
        print_only = True
        input_image_path = sys.argv[2]
        output_image_path = None
    elif sys.argv[1] == "--specific-exif":
        if len(sys.argv) < 3:
            print("使用方法: python exif_footer.py --specific-exif <input_image_path>")
            sys.exit(1)
        print_only = True
        specific_only = True
        input_image_path = sys.argv[2]
        output_image_path = None
    elif sys.argv[1] == "--specific-footer":
        if len(sys.argv) < 3:
            print(
                "使用方法: python exif_footer.py --specific-footer <input_image_path> [output_image_path]"
            )
            sys.exit(1)
        specific_footer = True
        input_image_path = sys.argv[2]
        # 出力ファイル名が指定されていない場合、元のファイル名に "_with_specific_exif" を付加
        if len(sys.argv) > 3:
            output_image_path = sys.argv[3]
        else:
            filename, ext = os.path.splitext(input_image_path)
            output_image_path = f"{filename}_with_specific_exif{ext}"
    else:
        input_image_path = sys.argv[1]

        # 出力ファイル名が指定されていない場合、元のファイル名に "_with_exif" を付加
        if len(sys.argv) > 2:
            output_image_path = sys.argv[2]
        else:
            filename, ext = os.path.splitext(input_image_path)
            output_image_path = f"{filename}_with_exif{ext}"

    # フッター画像とフォントのパス
    current_dir = os.path.dirname(os.path.abspath(__file__))

    img = Image.open(input_image_path)
    exif_data = get_exif_data(img)
    camera_make = exif_data.get("Make", "").upper()

    if "SONY" in camera_make:
        footer_image_path = os.path.join(current_dir, "./Assets/α.jpeg")
    elif "CANON" in camera_make:
        footer_image_path = os.path.join(current_dir, "./Assets/EOS.jpeg")
    else:  # Apple または他のメーカー（デフォルト）
        footer_image_path = os.path.join(current_dir, "./Assets/Apple.jpeg")

    font_path = os.path.join(current_dir, "./Fonts/SFPRODISPLAYBOLD.OTF")

    add_footer_with_exif(
        input_image_path,
        output_image_path,
        footer_image_path,
        font_path,
        print_only,
        specific_only,
        specific_footer,
    )


if __name__ == "__main__":
    main()
