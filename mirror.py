from PIL import Image, ImageDraw, ImageSequence
import math

def mirror_flip(image, l2r=True, vertical=False):
    width, height = image.size
    half_width = width // 2
    half_height = height // 2

    if vertical:
        top_half = image.crop((0, 0, width, half_height))
        bottom_half = image.crop((0, half_height, width, height))

        if l2r:
            mirrored_bottom = top_half.transpose(Image.FLIP_TOP_BOTTOM)
            new_image = Image.new('RGB', (width, height))
            new_image.paste(top_half, (0, 0))
            new_image.paste(mirrored_bottom, (0, half_height))
        else:
            mirrored_top = bottom_half.transpose(Image.FLIP_TOP_BOTTOM)
            new_image = Image.new('RGB', (width, height))
            new_image.paste(bottom_half, (0, half_height))
            new_image.paste(mirrored_top, (0, 0))
    else:
        left_half = image.crop((0, 0, half_width, height))
        right_half = image.crop((half_width, 0, width, height))

        if l2r:
            mirrored_right = left_half.transpose(Image.FLIP_LEFT_RIGHT)
            new_image = Image.new('RGB', (width, height))
            new_image.paste(left_half, (0, 0))
            new_image.paste(mirrored_right, (half_width, 0))
        else:
            mirrored_left = right_half.transpose(Image.FLIP_LEFT_RIGHT)
            new_image = Image.new('RGB', (width, height))
            new_image.paste(right_half, (half_width, 0))
            new_image.paste(mirrored_left, (0, 0))

    return new_image

def mirror_flip_image(input_path, output_path, l2r=True, vertical=False):
    image = Image.open(input_path)
    new_image = mirror_flip(image, l2r, vertical)
    new_image.save(output_path)

def mirror_flip_gif(input_path, output_path, l2r=True, vertical=False):
    with Image.open(input_path) as gif:
        frames = []

        for frame in ImageSequence.Iterator(gif):
            new_frame = mirror_flip(frame.convert("RGB"), l2r, vertical)
            frames.append(new_frame)

        frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0)

input_gif_path = 'target.gif'
output_gif_path = 'output.gif'
input_jpg_path = '1.jpg'
output_jpg_path = 'output.jpg'

# 使用示例
# mirror_flip_gif(input_gif_path, output_gif_path, l2r=False, vertical=True)
# mirror_flip_image(input_jpg_path, output_jpg_path, l2r=True, vertical=False)

def create_windmill_frame(blade_image, size, angle, enlarge=False):
    """
    offset: 控制图片向中心聚拢的距离，值越大，图片越靠近中心
    size: 最终图像的背景大小（正方形）
    blade_image: 原始传入的图片，保持宽高比不变
    """
    # 创建一个统一的背景，不再是透明
    background = Image.new("RGBA", (size, size), (0, 0, 0, 1))  # 背景为白色
    center = (size // 2, size // 2)

    # 根据原始图片的宽高比调整大小，保持宽高比不变
    max_width = size // 2
    max_height = size // 2
    aspect_ratio = blade_image.width / blade_image.height

    if aspect_ratio > 1:
        # 如果图片宽大于高，根据宽度缩放
        new_width = max_width
        new_height = int(max_width / aspect_ratio)
    else:
        # 如果图片高大于宽，根据高度缩放
        new_height = max_height
        new_width = int(max_height * aspect_ratio)
 # 如果需要放大，将尺寸放大1.1倍
    re_new_width = new_width
    re_new_height = new_height
    scale = 1.2
    if enlarge:
        re_new_width = int(new_width * scale)
        re_new_height = int(new_height * scale)
    resized_blade = blade_image.resize((re_new_width, re_new_height), Image.LANCZOS)

    # 计算四个图片的粘贴位置，并分别以0, 90, 180, 270度旋转
    blades = [
        resized_blade,  # 0度旋转
        resized_blade.rotate(-90, expand=True),  # 90度旋转
        resized_blade.rotate(-180, expand=True),  # 180度旋转
        resized_blade.rotate(-270, expand=True)  # 270度旋转
    ]
    offset = re_new_width - new_width
    offset_h = re_new_height - new_height
    offset2 = int(offset / 2)
    offset2_h = int(offset_h / 2)
    # 向中心偏移 offset 值，offset 为0时图片应放在四个角
    if blade_image.width > blade_image.height:
        positions = [
            (0 - offset, 0 + new_width - new_height - offset_h),  # 左上
            (size - new_width, 0 - offset),  # 右上
            (size - new_width, size - new_width),  # 右下
            (0 - offset_h + new_width - new_height, size - new_width)  # 左下
        ]
    else:
        positions = [
            (0 - new_width + new_height - offset, 0 - offset_h),  # 左上 --
            (size - new_height, 0 - new_width + new_height - offset),  # 右上+-
            (size - new_height, size - new_height),  # 右下++
            (0 - offset_h, size - new_height)  # 左下-+
        ]
    # 将四张图片粘贴到对应的位置
    for blade, pos in zip(blades, positions):
        background.paste(blade, pos, blade)

    # 旋转整个背景（包括四张图片）
    rotated_background = background.rotate(angle, resample=Image.BICUBIC)
    return rotated_background

def create_windmill_gif(input_path, output_path, size=450, frames=25, duration=60, clockwise=False):
    with Image.open(input_path) as blade_img:
        blade_img = blade_img.convert("RGBA")  # 确保图片有透明度
        gif_frames = []
        # 根据是否顺时针或逆时针旋转确定角度步进
        angle_step = -360 / frames if clockwise else 360 / frames

        for i in range(frames):
            angle = i * angle_step
            # 如果当前帧的角度不是90度的倍数，放大图片
            enlarge = (i * angle_step) % 90 != 0
            frame = create_windmill_frame(blade_img, size, angle, enlarge)
            gif_frames.append(frame)

        # 将所有帧转换为 P模式并设置透明度
        gif_frames = [frame.convert("P", palette=Image.ADAPTIVE) for frame in gif_frames]

        # 保存 GIF，并确保透明度，修改了持续时间为 50ms
        gif_frames[0].save(
            output_path,
            save_all=True,
            append_images=gif_frames[1:],
            loop=0,
            duration=duration,  # 每帧持续时间
            transparency=None,
            disposal=2,
            format="GIF"  # 确保以GIF格式保存
        )
