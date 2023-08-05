
from PIL import Image, ImageDraw, ImageFont, ImageOps
import piexif
import math
import os


def add_watermark(jpg_file, camera_name=None, black=False, is_img=False, logo='hasselblad.png'):
    """
    添加水印
    :param logo: 默认相机的logo
    :param camera_name: 手机名称
    :param black: 如果想水印背景是黑色 就填true  默认false
    :param is_img: 如果是单张图片就填True，默认False
    :param jpg_file: 每张图片的路径
    :return: 无（图片直接到本地）
    """
    background_color = (255, 255, 255) if not black else (0, 0, 0)
    fill_color = (0, 0, 0) if not black else (255, 255, 255)

    # 读取图片和EXIF信息
    image_path = os.path.join(jpg_file[0], jpg_file[1])
    image = Image.open(image_path)
    exif_data = image.info.get("exif")
    data = piexif.load(exif_data)

    # 根据方向信息旋转图片
    orientation = data["0th"].get(piexif.ImageIFD.Orientation)
    if orientation is not None and orientation != 1:
        print(orientation)
        image = ImageOps.exif_transpose(image)
    # 获取图片尺寸
    width, height = image.size
    # 计算新图片高度 长度+22%
    print(width)
    new_height = math.prod([width, 1.117])
    print(new_height)
    new_width = math.prod([width, 1.117])
    interval = int(math.prod([width, 0.117])/2)
    print(int(new_width))
    # 还原竖屏
    # 创建新的白色背景画布
    canvas = Image.new("RGB", (int(new_width),int(new_width)), background_color)
    # 将原始图片粘贴到新画布上
    canvas.paste(image, (interval, interval))
    # 获取新画布的宽高
    canvas_width, canvas_height = canvas.size

    # 添加文字
    def add_text(text, size, x, y, font=r"C:\Windows\Fonts\msyh.ttc", fill=fill_color, old_x=False):
        """
        :param text: 要添加的文字
        :param size: 文字大小：按图片高的比例1很小，10和图片水印一样大
        :param x: 文字在水印的位置，0在最左边 10在最右边
        :param y: 文字在水印的位置，0在最上面 10在最下面
        :param fill: 文字颜色 可接收参数格式：(255, 0, 0)# 红色、'#0000FF80'# 半透明蓝色、'black'、# 黑色、(128, 128, 128) # 中灰色
        :param old_x: 如果是True 表示传入的值是上次返回的，可以直接用的
        :param font:字体文件路径:
                    默认微软雅黑细体C:\Windows\Fonts\msyhl.ttc，
                    微软雅黑常规：C:\Windows\Fonts\msyh.ttc
                    机型和拍摄参数用微软雅黑粗体
                    黑体C:\Windows\Fonts\simhei.ttf是小米默认的但是间距很宽
        :return:x的值
        """
        draw = ImageDraw.Draw(canvas)
        text = text
        size = int(new_height * 0.01 * size)
        font = ImageFont.truetype(font, size=size)
        _, _, text_width, text_height = draw.textbbox((x, y), text, font=font)
        if not old_x:
            x = (width - text_width) * 0.1 * x
        y = height + ((new_height - height) - text_height) * 0.1 * y
        draw.text((x, y), text, fill=fill, font=font)
        return x

    def add_H():
        b_img = Image.open(r"watermark/" + "h.png")

        # 计算b_img缩放后的高度 和 调整b_img大小
        new_b_height = int(canvas_height * 0.085)
        b_img = b_img.resize((int(b_img.width * new_b_height / b_img.height), new_b_height))

        location = (int(canvas_height * 0.41), int(canvas_height * 0.854 - b_img.size[1]))
        try:
            canvas.paste(im=b_img, box=location, mask=b_img)  # 参数“mask”来确保透明通道被正确应用,没有该参数透明就会变成黑色
        except ValueError:
            canvas.paste(im=b_img, box=location)  # 有些水印没有透明通道

    def add_logo():
        b_img = Image.open(r"watermark/" + logo)

        # 计算b_img缩放后的高度 和 调整b_img大小
        new_b_height = int(canvas_height * 0.031)
        b_img = b_img.resize((int(b_img.width * new_b_height / b_img.height), new_b_height))

        location = (int(canvas_height * 0.275), int(canvas_height * 0.90 - b_img.size[1])+1)
        try:
            canvas.paste(im=b_img, box=location, mask=b_img)  # 参数“mask”来确保透明通道被正确应用,没有该参数透明就会变成黑色
        except ValueError:
            canvas.paste(im=b_img, box=location)  # 有些水印没有透明通道

    try:
        # 获取光圈值
        aperture_value = data['Exif'][piexif.ExifIFD.FNumber]
        aperture_fstop = aperture_value[0] / aperture_value[1]
        aperture = f'f/{aperture_fstop:.2f}'
        # logo
        add_H()
        add_logo()
        # 机型
        phone =data["0th"][piexif.ImageIFD.Model].decode('utf-8')
        add_text(f"Shot on {phone}",size=2.1, x=7.2, y=6.544, font=r"D:\F37Bolton-Regular.woff2.ttf")
        # 拍摄参数
        add_text(f"10Bit 480MP {aperture} IMX789", size=1.6, x=5.35, y=8.75,
                           font=r"D:\F37Bolton-Regular.woff2.ttf",fill=(79,79,79))


    except KeyError:
        print(jpg_file[1] + "获取的参数不全")
        return

    # 如果方向标记非1，则调整图像
    if orientation != 1:
        # 根据方向标记旋转或翻转图像
        if orientation == 2:
            canvas = canvas.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            # 上下翻转
            canvas = canvas.rotate(180)
        elif orientation == 4:
            canvas = canvas.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            canvas = canvas.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            # 旋转
            canvas = canvas.transpose(Image.ROTATE_90)
        elif orientation == 7:
            canvas = canvas.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            canvas = canvas.rotate(90)

    # 保存图片（保留EXIF信息）
    if is_img:  # 如果是单张图片
        canvas.save(os.path.join(jpg_file[0], jpg_file[1].replace('.jpg', '-加水印.jpg')), "JPEG", exif=exif_data)
    else:
        canvas.save(os.path.join(jpg_file[0] + "加水印", jpg_file[1]), "JPEG", exif=exif_data)


if __name__ == '__main__':
    folder_path = input('请输入jpg图片或文件夹路径')
    # 是否是文件夹
    if os.path.isdir(folder_path):
        # 要新建文件夹？
        if not os.path.isdir(folder_path + "加水印"):
            os.mkdir(folder_path + "加水印")
        # 拿到文件夹下面的jpg文件直接调用方法
        [add_watermark([folder_path, f]) for f in os.listdir(folder_path) if f.endswith('.jpg')]
    # 是否是单个文件
    elif os.path.isfile(folder_path) and folder_path.endswith('.jpg'):
        add_watermark([os.path.dirname(folder_path), os.path.basename(folder_path)],
                      is_img=True)
    else:
        print('路径有误')