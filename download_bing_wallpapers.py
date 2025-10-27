#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
下载Bing壁纸信息并保存为JSON文件，按年月分类
"""

import os
import re
import json
import requests
import datetime
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bing壁纸API
BING_API_URL = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=7&mkt=zh-CN"
BING_BASE_URL = "https://www.bing.com"

def get_bing_wallpapers():
    """
    获取Bing壁纸信息
    """
    try:
        logger.info("开始获取Bing壁纸信息...")
        response = requests.get(BING_API_URL)
        response.raise_for_status()
        data = response.json()
        
        wallpapers = []
        for image in data.get('images', []):
            # 提取壁纸信息
            # 构建4K图片URL (将1920x1080替换为UHD分辨率)
            url = BING_BASE_URL + image.get('url', '')
            # url_4k = url.replace('_1920x1080\.jpg.*', '_UHD.jpg')
            url_4k = re.sub(r'_1920x1080\.jpg.*', '_UHD.jpg', url)
            
            wallpaper = {
                'date': image.get('enddate', ''),
                'url_1080p': url,
                'url_4k': url_4k,
                'copyright': image.get('copyright', ''),
                'title': image.get('title', ''),
                'desc': image.get('desc', ''),
                'copyrightlink': image.get('copyrightlink', '')
            }
            wallpapers.append(wallpaper)
        
        logger.info(f"成功获取 {len(wallpapers)} 张壁纸信息")
        return wallpapers
    except Exception as e:
        logger.error(f"获取Bing壁纸信息失败: {str(e)}")
        return []

def save_wallpapers_by_month(wallpapers):
    """
    按年月保存壁纸信息到JSON文件
    """
    if not wallpapers:
        logger.warning("没有壁纸信息可保存")
        return
    
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    
    # 创建wallpapers目录
    wallpapers_dir = script_dir / "wallpapers"
    wallpapers_dir.mkdir(exist_ok=True)
    
    # 按年月分组壁纸
    wallpapers_by_month = {}
    for wallpaper in wallpapers:
        date_str = wallpaper.get('date', '')
        if len(date_str) == 8:  # 格式为YYYYMMDD
            year = date_str[:4]
            month = date_str[4:6]
            key = f"{year}{month}"
            
            if key not in wallpapers_by_month:
                wallpapers_by_month[key] = []
            
            wallpapers_by_month[key].append(wallpaper)
    
    # 保存每个月的壁纸信息
    for key, monthly_wallpapers in wallpapers_by_month.items():
        year = key[:4]
        month = key[4:6]
        
        # 创建年份目录
        year_dir = wallpapers_dir / year
        year_dir.mkdir(exist_ok=True)
        
        # 输出文件路径
        output_file = year_dir / f"{year}{month}.json"
        
        # 如果文件已存在，读取现有数据并合并
        existing_wallpapers = []
        if output_file.exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_wallpapers = json.load(f)
                logger.info(f"读取现有文件 {output_file}")
            except Exception as e:
                logger.error(f"读取文件 {output_file} 失败: {str(e)}")
        
        # 合并数据，避免重复
        existing_dates = {w.get('date') for w in existing_wallpapers}
        new_wallpapers = [w for w in monthly_wallpapers if w.get('date') not in existing_dates]
        
        if new_wallpapers:
            merged_wallpapers = existing_wallpapers + new_wallpapers
            
            # 按日期排序
            merged_wallpapers.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # 保存到文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(merged_wallpapers, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已更新 {output_file}，新增 {len(new_wallpapers)} 条数据")
        else:
            logger.info(f"文件 {output_file} 无需更新")

def main():
    """
    主函数
    """
    # 获取Bing壁纸信息
    wallpapers = get_bing_wallpapers()
    
    # 按年月保存壁纸信息
    save_wallpapers_by_month(wallpapers)
    
    logger.info("处理完成")

if __name__ == "__main__":
    main()