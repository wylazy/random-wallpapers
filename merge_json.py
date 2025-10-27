#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
合并wallpapers目录下的所有JSON文件到一个拍平的JSON文件
"""

import os
import json
import glob
from pathlib import Path

def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    
    # 输出文件路径
    output_file = script_dir / "all_wallpapers.json"
    
    # 存储所有壁纸数据
    all_wallpapers = []
    
    # wallpapers目录路径
    wallpapers_dir = script_dir / "wallpapers"
    
    print("开始合并JSON文件...")
    
    # 遍历年份目录
    for year_dir in sorted(wallpapers_dir.glob("*"), reverse=True):
        if year_dir.is_dir():
            # 获取该年份目录下的所有JSON文件
            json_files = list(year_dir.glob("*.json"))
            
            # 遍历每个JSON文件
            for json_file in sorted(json_files, reverse=True):
                print(f"处理文件: {json_file}")
                
                try:
                    # 读取JSON文件内容
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 将数据添加到总数组中
                    if isinstance(data, list):
                        all_wallpapers.extend(data)
                except Exception as e:
                    print(f"处理文件 {json_file} 时出错: {str(e)}")
    
    # 将合并后的数据写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_wallpapers, f, ensure_ascii=False, indent=2)
    
    print(f"合并完成! 共合并了 {len(all_wallpapers)} 条壁纸数据")
    print(f"输出文件: {output_file}")

if __name__ == "__main__":
    main()