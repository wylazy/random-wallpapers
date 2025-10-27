# Bing壁纸收集器

这个项目用于自动收集Bing每日壁纸的信息，并将其保存为JSON格式。

## 功能特点

- 自动获取Bing每日壁纸信息
- 提供高清(1920x1080)和4K(3840x2160)分辨率图片链接
- 按年月分类保存为JSON文件
- 支持下载指定年月的历史壁纸信息
- 支持获取超过16天的历史壁纸（通过归档网站获取）
- 使用GitHub Actions自动定期更新
- 自动合并所有壁纸数据到一个文件

## 文件说明

- `download_bing_wallpapers.py`: 下载Bing壁纸信息并按年月保存
- `download_history_wallpapers.py`: 下载指定年月的历史壁纸信息
- `merge_json.py`: 合并所有壁纸数据到一个文件
- `.github/workflows/update_wallpapers.yml`: GitHub Actions自动化工作流配置

## 使用方法

### 手动运行

```bash
# 下载当前Bing壁纸信息
python download_bing_wallpapers.py

# 下载指定年月的历史壁纸信息（支持超过16天的历史壁纸）
python download_history_wallpapers.py --year 2023 --month 05

# 合并所有壁纸数据
python merge_json.py

# 生成函数
python generate_functions.py

```

### 自动更新

本项目配置了GitHub Actions工作流，会自动执行以下操作：

1. 每天自动运行，获取最新的Bing壁纸信息
2. 按年月保存到对应的JSON文件
3. 更新合并后的壁纸数据文件
4. 自动提交更改到GitHub仓库

## 数据格式

每个壁纸信息包含以下字段：

```json
{
  "date": "YYYYMMDD",
  "url_1080p": "壁纸URL(1920x1080)",
  "url_4k": "壁纸4K URL(3840x2160)",
  "urlbase": "壁纸基础URL",
  "copyright": "版权信息",
  "title": "标题",
  "desc": "描述",
  "copyrightlink": "版权链接"
}
```

## 目录结构

```
WallPapers/
├── download_bing_wallpapers.py
├── merge_json.py
├── all_wallpapers.json
├── wallpapers/
│   ├── YYYY/
│   │   ├── YYYYMM.json
```

## 部署到 EdgeOnes

### 自动部署
1.  Fork 本项目到你的 GitHub 账号
2.  在 EdgeOnes 中创建一个新的项目
3.  连接你的 GitHub 账号到 EdgeOnes
4.  在 EdgeOnes 中配置项目，选择你的 Fork 后的仓库
5.  配置 GitHub Actions 工作流，选择 `update_wallpapers.yml`
6.  手动触发一次工作流，确保配置正确
7.  配置定时触发，例如每天凌晨2点运行

### 手动部署
1. 下载项目到本地
2. 将 functions 和 index.html 压缩为一个 zip 文件
3. 在 EdgeOnes 中创建一个新的 Pages 项目
4. 上传压缩后的 zip 文件到 EdgeOnes
5. 部署项目

### 随机图片 API
```
GET /random_wallpaper?resolution=4k # 随机获取一张获取 4K 图片
GET /random_wallpaper?resolution=1080p # 随机获取一张获取 1080P 图片
```

## 许可证

MIT
