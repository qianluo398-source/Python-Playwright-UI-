import pytest
from pages.login_page import LoginPage
from typing import Any, List
from playwright.sync_api import BrowserContext, Error, Page
import allure
import os
from slugify import slugify
from typing import Dict


def _build_artifact_test_folder(pytestconfig: Any, request: pytest.FixtureRequest, folder_or_file_name: str) -> str:
    output_dir = pytestconfig.getoption("--output")
    return os.path.join(output_dir, slugify(request.node.nodeid), folder_or_file_name)


@pytest.fixture(scope="session")
def login_first(context, base_url, pytestconfig) -> None:
    """有些网站网页关闭cookie就失效了，全局登录一次"""
    # context = browser.new_context(base_url=base_url, no_viewport=True)
    print("base_url----", base_url)
    page = context.new_page()
    LoginPage(page).navigate()
    LoginPage(page).login("py", "123456")
    # 等待登录成功页面重定向
    page.wait_for_url(url='**/index.html')


@pytest.fixture(scope="module")
def unlogin_context(browser, base_url, pytestconfig, browser_context_args: Dict):
    """
    登录注册页面（不依赖于先登录）单独创建独立的 context 上下文
    避免全局先登录加载cookie，导致有些打开登录页直接跳到首页去了
    :return:
    """
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture
def unlogin_page(unlogin_context: BrowserContext, pytestconfig: Any, request: pytest.FixtureRequest):
    """
    登录注册页面（不依赖于先登录）单独创建独立的 page 对象
    带上用例失败截图和添加视频功能
    """
    pages: List[Page] = []
    unlogin_context.on("page", lambda page: pages.append(page))
    page = unlogin_context.new_page()
    yield page
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else True
    # 截图判断
    screenshot_option = pytestconfig.getoption("--screenshot")
    capture_screenshot = screenshot_option == "on" or (failed and screenshot_option == "only-on-failure")
    print(f"capture_screenshot:{capture_screenshot}")
    if capture_screenshot:
        for index, page in enumerate(pages):
            human_readable_status = "failed" if failed else "finished"
            screenshot_path = _build_artifact_test_folder(
                pytestconfig, request, f"test-{human_readable_status}-{index + 1}.png"
            )
            print(f'-----------------{screenshot_path}')
            try:
                page.screenshot(timeout=5000, path=screenshot_path)
                # 把截图放入allure报告
                allure.attach.file(screenshot_path,
                                   name=f"{request.node.name}-{human_readable_status}-{index + 1}",
                                   attachment_type=allure.attachment_type.PNG
                                   )
            except Error:
                pass
    page.close()
    # 用例添加视频
    video_option = pytestconfig.getoption("--video")
    preserve_video = video_option == "on" or (failed and video_option == "retain-on-failure")
    if preserve_video:
        for page in pages:
            video = page.video
            if not video:
                continue
            try:
                video_path = video.path()
                file_name = os.path.basename(video_path)
                file_path = _build_artifact_test_folder(pytestconfig, request, file_name)
                video.save_as(path=file_path)
                # 放入视频
                allure.attach.file(file_path, name=f"{request.node.name}-{human_readable_status}-{index + 1}",
                                   attachment_type=allure.attachment_type.WEBM)
            except Error:
                # Silent catch empty videos.
                pass
