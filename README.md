# web UI自动化测试

基于Playwright+pytest的UI自动化测试框架

**首先安装本项目所需的依赖库，cmd命令为：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r E:
\playwright\requirements.txt
其中：E:\playwright路径替换自己项目的磁盘路径。**

playwright帮助官网：https://playwright.net.cn/python/docs/intro

----

## 模块类的设计说明

`cases` 测试用例集

`mocks` mock数据集

`pages` 封装的页面元素

`plugins` 二开扩展插件

`conftest.py` pytest配置文件

`reports` 测试报告临时文件

`test-results` 测试报告截图、视频的临时文件

`allure_report` 生成的allure测试报告

`run.py` 框架运行入口

`requirements.txt` 项目环境运行所需的第三方库

`pytest.ini` 测试框架的配置文件，制定运行规则

----

## 安装驱动

### 安装浏览器驱动：Chrome、Firefox、WebKit

playwright install

#### 也可以单独安装，例如只安装Chrome浏览器驱动

playwright install chromium

#### 卸载浏览器驱动

playwright uninstall --all

### 执行命令

#### 运行框架

运行run.py

或者命令行执行pytest --alluredir ./reports

### 查看、生成allure报告

使用命令行运行时，生成报告

allure serve ./reports

查看报告：allure_report/index.html

### 测试结果追踪trace

--tracing=on 设置每个用例都捕获日志

--tracing=retain-on-failure 仅用例失败的时候捕获日志

日志追踪的方式：

1、访问解析的网站：https://trace.playwright.dev/

选择日志文件test-results/trace.zip解析

2、命令行执行

playwright show-trace test-results/trace.zip

### playwright脚本录制

命令行启动

playwright codegen http://47.116.12.183/login.html