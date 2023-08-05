# By：仰晨
# 文件名：批量加大水印
# 时 间：2023/5/10 18:43

from PIL import Image, ImageDraw, ImageFont, ImageOps
import piexif
import os


def add_watermark(jpg_file, camera_name=None, black=False, is_img=False, place="在宇宙一颗蔚蓝的星球上", logo='yc.png'):
    """
    添加水印
    :param logo: 默认相机的logo
    :param place: 当照片里面读取不到照片的时候就用这个值代替，默认值“在宇宙一颗蔚蓝的星球上"
    :param camera_name: 相机名字 因为有一些相机名字不是正常的手机名字，这时可以传入自定义
    :param black: 如果想水印背景是黑色 就填true  默认false
    :param is_img: 如果是单张图片就填True，默认False
    :param jpg_file: 每张图片的路径
    :return: 无（图片直接到本地）
    """
    background_color = (255, 255, 255) if not black else (0, 0, 0)
    fill_color = (0, 0, 0) if not black else (255, 255, 255)
    small_text_color = (134, 134, 134) if not black else (255, 255, 255)

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
    # 计算新图片高度 长度+11.5%
    new_height = int(height * 1.115)  # 还原竖屏
    # new_height = int(height * 1.156)  # 还原横屏
    # 创建新的白色背景画布
    canvas = Image.new("RGB", (width, new_height), background_color)
    # 将原始图片粘贴到新画布上
    canvas.paste(image, (0, 0))
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
        size = int(height * 0.01 * size)
        font = ImageFont.truetype(font, size=size)  # 请确保你有正确的字体文件路径"arial.ttf", size=20
        # textbbox() 方法返回一个包括文本四个顶点坐标的元组: (左侧x坐标,  顶部y坐标,  右侧x坐标,  底部y坐标)
        _, _, text_width, text_height = draw.textbbox((x, y), text, font=font)
        if not old_x:
            x = (width - text_width) * 0.1 * x
        y = height + ((new_height - height) - text_height) * 0.1 * y
        draw.text((x, y), text, fill=fill, font=font)
        return x

    # 加一竖
    def add_line(x):
        """
        给水印图片和文字之间的分割线
        :param x: 已经计算好的要贴在目标图片的x轴的坐标
        :return:
        """
        # 创建一个10*240，颜色为#ddd的新图像 # 直接计算b_img缩放后的高度
        line_width, line_height = int(canvas_height * 0.05 / 30), int(canvas_height * 0.04)
        line_img_color = (211, 211, 211) if not black else (51, 51, 51)
        line_img = Image.new("RGB", (line_width, line_height), color=line_img_color)

        # 粘贴b_img到a_img右下角
        location = (int(x - line_img.size[0] * 6), int(canvas_height * 0.97 - line_img.size[1]))
        canvas.paste(im=line_img, box=location)

    def add_logo(x):
        b_img = Image.open(r"watermark/" + logo)

        # 计算b_img缩放后的高度 和 调整b_img大小
        new_b_height = int(canvas_height * 0.045)
        b_img = b_img.resize((int(b_img.width * new_b_height / b_img.height), new_b_height))

        # 粘贴b_img到a_img右下角
        location = (int(x - b_img.size[0] - b_img.size[0] * 0.5), int(canvas_height * 0.974 - b_img.size[1]))
        try:
            canvas.paste(im=b_img, box=location, mask=b_img)  # 参数“mask”来确保透明通道被正确应用,没有该参数透明就会变成黑色
        except ValueError:
            canvas.paste(im=b_img, box=location)  # 有些水印没有透明通道

    try:
        # 获取快门速度or曝光时间 [s]
        shutter_speed_value = data["Exif"][piexif.ExifIFD.ExposureTime]
        shutter_speed = f"1/{round(float(shutter_speed_value[1]) / float(shutter_speed_value[0]))}"
        # 获取光圈值
        aperture_value = data['Exif'][piexif.ExifIFD.FNumber]
        aperture_fstop = aperture_value[0] / aperture_value[1]
        aperture = f'f/{aperture_fstop:.2f}'
        # 获取 ISO 感光度
        iso = "IOS" + str(data["Exif"][piexif.ExifIFD.ISOSpeedRatings])

        def get_gps():
            """
            获取拍摄位置
            :return: 如果有就返回gps位置，没有就写字
            """
            try:
                gps_N = data['GPS'][2]
                gps_N = f"{gps_N[0][0] / gps_N[0][1]:02.0f}°{int(gps_N[1][0] / gps_N[1][1])}\'{int(gps_N[2][0] / gps_N[2][1])}\"N"
                gps_E = data['GPS'][4]
                gps_E = f"{gps_E[0][0] / gps_E[0][1]:02.0f}°{int(gps_E[1][0] / gps_E[1][1])}\'{int(gps_E[2][0] / gps_E[2][1])}\"E"
                return f"{gps_N}  {gps_E}"
            except KeyError:
                return place

        # 机型
        # x_value = add_text(data["0th"][piexif.ImageIFD.Model].decode('utf-8') if camera_name is None else camera_name,
        #                    size=2.1, x=0.35, y=3, font=r"C:\Windows\Fonts\msyhbd.ttc")
        x_value = add_text("",
                           size=2.1, x=0.35, y=3, font=r"C:\Windows\Fonts\msyhbd.ttc")
        # 拍摄时间
        add_text(data["0th"][piexif.ImageIFD.DateTime].decode('utf-8'), size=1.55, x=x_value, fill=small_text_color,
                 old_x=True, y=6.5)
        # 拍摄参数
        x_value = add_text(f"{aperture} {shutter_speed} {iso}", size=2.1, x=9.5, y=3.2,
                           font=r"C:\Windows\Fonts\msyhbd.ttc")
        # 拍摄位置
        add_text(get_gps(), size=1.55, x=x_value, fill=small_text_color, old_x=True, y=6.7)
        # 分割线
        add_line(x_value)
        # logo
        add_logo(x_value)

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
    elif os.path.isfile(folder_path) and folder_path.endswith('.jpg'):  #
        add_watermark([os.path.dirname(folder_path), os.path.basename(folder_path)],
                      is_img=True)  # , black=True, camera_name="Mi 11 Pro"
    else:
        print('路径有误')