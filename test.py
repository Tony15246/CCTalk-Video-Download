import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor

import requests
from tqdm import tqdm


def transform_password(password):
    md5_hash = hashlib.md5()
    md5_hash.update(password.encode("utf-8"))
    hashed_password = md5_hash.hexdigest()
    return hashed_password


def transform_phone(phone):
    result = ""

    for num in phone:
        char = chr(ord("C") + int(num))  # C的ASCII值是67
        result += f"01{char}"

    return result


def get_cookie(phone, password):
    phone = transform_phone(phone)
    password = transform_password(password)
    url = "https://pass.cctalk.com/Handler/UCenter"
    params = {"action": "Login", "encrypt": 1, "hc": phone, "password": password}
    response = requests.get(url, params=params, timeout=5)
    return response.json()["Data"]["Cookie"]


def get_group_list(cookie):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Cookie": f"ClubAuth={cookie}",
    }
    url = "https://m.cctalk.com/webapi/content/v1.1/user/my_group_list"
    response = requests.get(url, headers=headers, timeout=5)
    data = response.json()
    item_list = []
    for item in data["data"]["items"]:
        group_id = item["groupId"]
        group_name = item["groupName"]
        item_dict = {"id": group_id, "name": group_name}
        item_list.append(item_dict)
    return item_list


def get_series_list(cookie, group_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Cookie": f"ClubAuth={cookie}",
    }
    url = f"https://www.cctalk.com/webapi/content/v1.2/series/group/{group_id}/series"
    params = {"limit": 10, "start": 0}
    response = requests.get(url, headers=headers, params=params, timeout=5)
    data = response.json()
    series_list = []
    for series in data["data"]["items"]:
        series_id = series["seriesId"]
        series_name = series["seriesName"]
        series_dict = {"id": series_id, "name": series_name}
        series_list.append(series_dict)
    return series_list


def get_movie_list(cookie, series_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Cookie": f"ClubAuth={cookie}",
    }
    url = "https://www.cctalk.com/webapi/content/v1.2/series/all_lesson_list"
    params = {"seriesId": series_id}
    response = requests.get(url, headers=headers, params=params, timeout=5)
    data = response.json()
    movie_list = []
    for movie in data["data"]["items"]:
        movie_id = movie["videoInfo"]["videoId"]
        movie_name = movie["videoInfo"]["videoName"]
        movie_dict = {"id": movie_id, "name": movie_name}
        movie_list.append(movie_dict)
    return movie_list


def get_download_url(cookie, movie_id):
    params = {"videoId": str(movie_id)}
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Cookie": f"ClubAuth={cookie}",
    }
    url = "https://www.cctalk.com/webapi/content/v1.1/video/detail"
    response = requests.get(url, headers=headers, params=params, timeout=5)
    return response.json()["data"]["videoUrl"]


def download_movies(cookie, movie_list):
    for index, movie in enumerate(movie_list):
        download_url = get_download_url(cookie, movie["id"])
        print(
            f"Index: {index}, ID: {movie['id']}, Name: {movie['name']}, Link: {download_url}"
        )

        response = requests.get(download_url, stream=True, timeout=300)
        total_size = int(response.headers.get("content-length", 0))  # 获取文件总大小
        block_size = 1024  # 每次读取的块大小（1KB）

        os.makedirs("./data/", exist_ok=True)
        with open(f"./data/{index + 1}. {movie["name"]}.mp4", "wb") as f, tqdm(
            desc=movie["name"],
            total=total_size,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for data in response.iter_content(block_size):
                f.write(data)
                progress_bar.update(len(data))  # 更新进度条

        print(f"{movie['name']}.mp4下载完成")


if __name__ == "__main__":
    with open("config.json", "r", encoding="utf8") as file:
        config = json.load(file)
    cookie = get_cookie(config["phone"], config["password"])
    item_list = get_group_list(cookie)
    for index, item in enumerate(item_list):
        print(f"Index: {index}, ID: {item['id']}, Name: {item['name']}")
    lesson_index = int(input("选择课程: "))
    group_id = item_list[lesson_index]["id"]
    series_list = get_series_list(cookie, group_id)
    for index, series in enumerate(series_list):
        print(f"Index: {index}, ID: {series['id']}, Name: {series['name']}")
    series_index = int(input("选择课程: "))
    series_id = series_list[series_index]["id"]
    movie_list = get_movie_list(cookie, series_id)
    download_movies(cookie, movie_list)
