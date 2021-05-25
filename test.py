from PIL import Image
import numpy as np


def convert(filename):
    print("[+] 只有png和bmp文件支持二值图像")
    Image.open(filename).convert('1').save(filename)


def encode(sourcefile, targetfile, secretfile):
    with open(secretfile) as f:
        secret = f.read()

    secret_bin = ""
    for c in secret:
        # 补到八位
        secret_bin += str(bin(ord(c)))[2:].rjust(8, '0')
    # print(secret_bin)
    source = Image.open(sourcefile)
    if source.mode != "1":
        print("[!] 非二值图像，无法进行信息隐藏，使用convert函数进行图像转换")
        exit(1)
    # 记一下行数到时候好还原图片
    row = len(np.array(source))
    # 数组拉到一维
    image_content = np.array(source).reshape(-1)
    first_pixel = image_content[0]
    cnt = 0
    distance = []
    # 统计游程
    for p in image_content:
        if p == first_pixel:
            cnt += 1
        else:
            distance.append(cnt)
            cnt = 1
            first_pixel = p
    # 把最后一个游程也加上去
    distance.append(cnt)

    # 插入数据
    first_pixel = image_content[0]
    if len(secret_bin) > len(distance):
        print("[!] 游程数过少，信息无法完全写入")
    else:
        # 向右补充到和游程数一致，防止出现无效信息直接全部填0截断掉
        index = -1  # 下标从0开始
        for i in range(len(secret_bin)):
            # 每次翻转当前的数据类型并移动下标
            index += distance[i]
            first_pixel = not first_pixel
            # 隐藏信息为0但游程为奇数 或 隐藏信息为1但游程为偶数
            if (int(secret_bin[i]) == 0 and distance[i] % 2 != 0) or (int(secret_bin[i]) == 1 and distance[i] % 2 == 0):
                # 把目前下标指的那位颜色翻转
                image_content[index] = first_pixel
                # 下一个游程变长一位
                distance[i + 1] += 1
                # 下标后退一位
                index -= 1

    Image.fromarray(image_content.reshape(row, -1)).save(targetfile)


def decode(sourcefile):
    image = Image.open(sourcefile)
    if image.mode != "1":
        print("[!] 非二值图像，信息隐藏结果提取可能有误")
    image_content = np.array(image).reshape(-1)
    first_pixel = image_content[0]
    cnt = 0
    result = ''
    for p in image_content:
        if first_pixel == p:
            cnt += 1
        else:
            first_pixel = p
            result += str(cnt % 2)
            cnt = 1
    # print(result)
    result = result[:len(result) - len(result) % 8]
    plain = ""
    for i in range(0, len(result), 8):
        plain += chr(int(result[i:i+8], 2))
    # 丢弃不可见字符
    for i in range(len(plain)):
        if not plain[i].isprintable():
            return plain[:i]
    return plain


# convert("source.png")
# encode("source.png", "result.png", "secret.txt")
plain_origin = decode("result.png")
print("[+] 原始加密图片解密: " + plain_origin)
plain_screenshot = decode("screenshot.png")
print("[+] 图片截图后解密: " + plain_screenshot)
plain_rotate = decode("rotation.png")
print("[+] 图片旋转后解密: " + plain_rotate)
plain_convert = decode("convert.png")
print("[+] 图片转换格式后解密: " + plain_convert)
plain_crop = decode("crop.png")
print("[+] 裁剪后的图像解密:" + plain_crop)

