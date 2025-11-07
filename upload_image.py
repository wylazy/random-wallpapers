import argparse
import json
import time
import requests
import subprocess
import os
import hashlib
import hmac
import base64
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from email.utils import formatdate

def get_content_type(file_name):
    """
    根据文件扩展名返回相应的content-type
    """
    extension = os.path.splitext(file_name)[1].lower()

    image_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.tiff': 'image/tiff',
        '.ico': 'image/x-icon'
    }

    return image_types.get(extension, 'application/octet-stream')

def upload_images():
    parser = argparse.ArgumentParser(description='Upload images to S3')
    parser.add_argument('--upload-limit', type=int, default=1, help='Limit number of images to upload (0 for all)')
    parser.add_argument('--aws-access-key-id', required=True, help='AWS Access Key ID')
    parser.add_argument('--aws-secret-access-key', required=True, help='AWS Secret Access Key')
    parser.add_argument('--endpoint-url', required=True, help='S3 Endpoint URL')
    parser.add_argument('--bucket-name', required=True, help='S3 Bucket Name')

    args = parser.parse_args()
    if not args.endpoint_url:
        print('No endpoint URL provided')
        return

    # 读取图片信息
    with open('./all_wallpapers.json', 'r', encoding='utf-8') as f:
        wallpapers = json.load(f)

    # 根据upload-limit决定上传数量
    if args.upload_limit > 0:
        wallpapers = wallpapers[:args.upload_limit]

    # 处理每个壁纸
    for wallpaper in wallpapers:
        try:
            date_str = wallpaper['date']
            url_4k = wallpaper['url_4k']

            # 解析日期获取年月
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            year = date_obj.year
            month = date_obj.month

            # 从URL获取对象名称
            parsed_url = urlparse(url_4k)
            query_params = parse_qs(parsed_url.query)
            object_name = query_params.get('id', [os.path.basename(parsed_url.path)])[0]
            key = f"{year}/{month:02d}/{object_name}"

            # 检查对象是否已存在
            try:
                # 生成签名用于检查对象是否存在
                date = formatdate(timeval=None, localtime=False, usegmt=True)
                resource = f"/{args.bucket_name}/{key}"
                
                # 构造待签名字符串 (HEAD请求)
                string_to_sign = f"HEAD\n\n\n{date}\n{resource}"
                
                # 计算签名
                signature = base64.b64encode(hmac.new(
                    args.aws_secret_access_key.encode('utf-8'),
                    string_to_sign.encode('utf-8'),
                    hashlib.sha1
                ).digest()).decode()

                # 使用curl检查对象是否存在
                check_cmd = [
                    'curl', '-I', '-X', 'HEAD',
                    f"{args.endpoint_url}/{args.bucket_name}/{key}",
                    '-H', f"Date: {date}",
                    '-H', f"Authorization: AWS {args.aws_access_key_id}:{signature}"
                ]

                result = subprocess.run(check_cmd, capture_output=True, text=True)
                outs = result.stdout.split('\n')
                status_line = outs[0] if len(outs) > 0 else ''
                if result.returncode == 0 and '200' in status_line:
                    print(f"Object {key} already exists in bucket {args.bucket_name}, skipping...")
                    continue
            except Exception as e:
                # 判断异常
                print(f"Error checking if object {key} exists: {str(e)}")
                pass

            # 获取图片数据
            print(f"Downloading {url_4k}")
            response = requests.get(url_4k)
            response.raise_for_status()
            image_bytes = response.content

            # 保存临时文件
            temp_file = f"temp_{object_name}"
            with open(temp_file, 'wb') as f:
                f.write(image_bytes)

            # 生成签名用于上传
            date = formatdate(timeval=None, localtime=False, usegmt=True)
            content_type = get_content_type(object_name)
            resource = f"/{args.bucket_name}/{key}"

            # 构造待签名字符串 (PUT请求)
            string_to_sign = f"PUT\n\n{content_type}\n{date}\n{resource}"

            # 计算签名
            signature = base64.b64encode(hmac.new(
                args.aws_secret_access_key.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha1
            ).digest()).decode()

            # 使用curl上传到S3
            print(f"Uploading to S3 with curl")
            upload_cmd = [
                'curl', '-i', '-X', 'PUT',
                '-T', temp_file,
                f"{args.endpoint_url}/{args.bucket_name}/{key}",
                '-H', f"Date: {date}",
                '-H', f"Content-Type: {content_type}",
                '-H', f"Authorization: AWS {args.aws_access_key_id}:{signature}"
            ]

            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Uploaded {object_name} to {args.bucket_name}/{key}")
            else:
                print(f"Error uploading {object_name}: {result.stderr}")

            # 删除临时文件
            os.remove(temp_file)

        except Exception as e:
            print(f"Error processing {wallpaper.get('date', 'unknown')}: {str(e)}")
            time.sleep(30)

if __name__ == "__main__":
    upload_images()
