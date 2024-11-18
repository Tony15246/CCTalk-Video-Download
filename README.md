## 脚本功能
下载cctalk上已购买过的课程到本地。这个项目并没有任何破解的成分，因为你已经购买过了的课程，才支持下载。

## 使用方法
在`test.py`同级目录下创建`config.json`文件，本件内容为账号的手机号和密码，格式如下。
``` json
{
    "phone": "xxxxxxxxxxx",
    "password": "xxxxxxxx"
}
```
使用如下命令安装依赖
```
pip install -r requirements.txt
```
使用如下命令运行脚本
```
python test.py
```
