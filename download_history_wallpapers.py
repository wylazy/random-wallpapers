#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
下载指定年月的Bing历史壁纸信息
"""

import os
import json
import requests
import argparse
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
BING_BASE_URL = "https://www.bing.com"

def get_bing_history_wallpapers(year, month, count=31):
    """
    获取指定年月的Bing历史壁纸信息
    
    参数:
        year: 年份，如2023
        month: 月份，如01、02...12
        count: 获取的壁纸数量，默认31（一个月最多31天）
    """
    wallpapers = []
    
    # 计算当前日期与目标日期的差值
    today = datetime.date.today()
    target_year_month = f"{year}{month}"
    current_year_month = today.strftime("%Y%m")

    # 计算目标月的天数
    days_in_month = get_days_in_month(int(year), int(month))
    logger.info(f"{year}年{month}月有{days_in_month}天")
    
    # 遍历每一天，获取壁纸信息
    for day in range(1, days_in_month + 1):
        day_str = f"{day:02d}"
        date_str = f"{year}{month}{day_str}"
        
        # 计算idx值（与当前日期的天数差）
        try:
            target_date = datetime.date(int(year), int(month), int(day_str))
            delta = (today - target_date).days
            
            if delta < 0:
                logger.warning(f"日期 {date_str} 在未来，跳过")
                continue
                
            # Bing API只能获取最近16天的壁纸，从第 3 方获取
            wallpaper = get_archived_wallpaper(date_str)

            if wallpaper and wallpaper.get('date') == date_str:
                wallpapers.append(wallpaper)
                logger.info(f"成功获取 {date_str} 的壁纸信息")
            else:
                logger.warning(f"未找到 {date_str} 的壁纸信息")
                
        except Exception as e:
            logger.error(f"获取 {date_str} 的壁纸信息失败: {str(e)}")
    
    logger.info(f"成功获取 {len(wallpapers)} 张壁纸信息")
    return wallpapers

def get_days_in_month(year, month):
    """获取指定年月的天数"""
    if month == 12:
        next_month = datetime.date(year + 1, 1, 1)
    else:
        next_month = datetime.date(year, month + 1, 1)
    
    last_day = next_month - datetime.timedelta(days=1)
    return last_day.day

def get_archived_wallpaper(date_str):
    """尝试从归档获取壁纸信息（针对超过16天的历史壁纸）"""
    try:
        # 从日期字符串中提取年月日
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        # 从bing.wdbyte.com获取历史壁纸 - 使用新的URL格式
        try:
            # 新的URL格式
            archive_url = f"https://bing.wdbyte.com/day/{year}{month}/{day}.html"
            logger.info(f"尝试从归档网站获取壁纸信息: {archive_url}")
            response = requests.get(archive_url, timeout=10)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 根据新的HTML结构提取信息
                # 提取标题和版权信息
                date_elem = soup.select_one('.w3-display-bottomleft h1.w3-xlarge')
                copyright_elem = soup.select_one('.w3-display-bottomleft p.w3-large')
                
                # 提取图片URL (4K和1080P)
                url_4k_elem = soup.select_one('.w3-display-topright a[target="_blank"]:nth-of-type(1)')
                url_1080p_elem = soup.select_one('.w3-display-topright a[target="_blank"]:nth-of-type(2)')
                
                if url_4k_elem and url_1080p_elem:
                    # 提取URL并清理空格
                    url_4k = url_4k_elem['href'].strip()
                    url_1080p = url_1080p_elem['href'].strip()
                    
                    # 确保URL是完整的
                    if not url_4k.startswith('http'):
                        url_4k = 'https:' + url_4k
                    if not url_1080p.startswith('http'):
                        url_1080p = 'https:' + url_1080p
                    
                    # 提取标题和版权信息
                    date_text = date_elem.text.strip() if date_elem else f"{year}-{month}-{day}"
                    copyright_text = copyright_elem.text.strip() if copyright_elem else ""
                    title = f"Bing Wallpaper {date_text}"
                    
                    logger.info(f"成功从归档网站获取壁纸信息: {title}")
                    
                    return {
                        'date': date_str,
                        'url_1080p': url_1080p,
                        'url_4k': url_4k,
                        'copyright': copyright_text,
                        'title': title,
                        'desc': "",
                        'copyrightlink': archive_url
                    }
        except Exception as e:
            logger.warning(f"从归档网站获取壁纸失败: {str(e)}")
            return None
        # 如果无法从归档网站获取，使用预测的URL和基本信息
    except Exception as e:
        logger.error(f"获取归档壁纸信息失败: {str(e)}")
        return None

def save_wallpapers(wallpapers, year, month):
    """保存壁纸信息到JSON文件"""
    if not wallpapers:
        logger.warning("没有壁纸信息可保存")
        return
    
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    
    # 创建wallpapers目录
    wallpapers_dir = script_dir / "wallpapers"
    wallpapers_dir.mkdir(exist_ok=True)
    
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
    new_wallpapers = [w for w in wallpapers if w.get('date') not in existing_dates]
    
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
    """主函数"""
    parser = argparse.ArgumentParser(description='下载指定年月的Bing历史壁纸信息')
    parser.add_argument('--year', type=str, required=True, help='年份，如2023')
    parser.add_argument('--month', type=str, required=True, help='月份，如01、02...12')
    args = parser.parse_args()
    
    # 验证输入
    if not args.year.isdigit() or len(args.year) != 4:
        logger.error("年份格式错误，应为4位数字，如2023")
        return
    
    if not args.month.isdigit() or len(args.month) != 2 or int(args.month) < 1 or int(args.month) > 12:
        logger.error("月份格式错误，应为2位数字，如01、02...12")
        return
    
    # 获取指定年月的壁纸信息
    wallpapers = get_bing_history_wallpapers(args.year, args.month)
    
    # 保存壁纸信息
    save_wallpapers(wallpapers, args.year, args.month)
    logger.info("处理完成")

if __name__ == "__main__":
    main()