from pages.login_page import LoginPage
from playwright.sync_api import expect, Page
import pytest


class TestLogin:
    """登录功能"""

    @pytest.fixture(autouse=True)
    def start_for_each(self, unlogin_page: Page):
        """
        登录功能用独立的上下文环境，不加载cookie
        :param unlogin_page: 独立上下文
        :return: None
        """
        print("for each--start: 打开新页面访问登录页")
        self.login = LoginPage(unlogin_page)
        self.login.navigate()
        yield
        print("for each--end: 后置操作")

    def test_login_1(self):
        """用户名为空，点注册"""
        self.login.fill_username('')
        self.login.fill_password('123456')
        self.login.click_login_button()
        # 断言
        expect(self.login.locator_username_tip1).to_be_visible()
        expect(self.login.locator_username_tip1).to_contain_text("不能为空")

    def test_login_2(self):
        """用户名大于30字符"""
        self.login.fill_username('hello world hello world hello world')
        # 断言
        expect(self.login.locator_username_tip2).to_be_visible()
        expect(self.login.locator_username_tip2).to_contain_text("用户名称1-30位字符")
        # 断言 登录按钮不可点击
        expect(self.login.locator_login_btn).not_to_be_enabled()

    def test_login__3(self):
        """用户名有特殊字符"""
        self.login.fill_username('hello!@#')
        # 断言
        expect(self.login.locator_username_tip3).to_be_visible()
        expect(self.login.locator_username_tip3).to_contain_text("用户名称不能有特殊字符,请用中英文数字")
        # 断言 注册按钮不可点击
        expect(self.login.locator_login_btn).not_to_be_enabled()

    @pytest.mark.parametrize("username,password,title", [
        ['py', '12345678', '输入错误的密码'],
        ['py11', '12345678', '输入错误的账号'],
    ])
    def test_login_error(self, username: str, password: str, title: str):
        """登录失败场景"""
        self.login.fill_username('py')
        self.login.fill_password('12345678')
        self.login.click_login_button()
        # 断言提示语可见
        expect(self.login.locator_login_error).to_be_visible()

    def test_login_success_1(self):
        """登录成功，断言url 和title"""
        self.login.fill_username("py")
        self.login.fill_password('123456')
        self.login.click_login_button()
        expect(self.login.page).to_have_title("首页")
        expect(self.login.page).to_have_url("/index.html")

    def test_login_success_2(self):
        """登录正常流程"""
        self.login.fill_username("py")
        self.login.fill_password('123456')
        # page.expect_ 显示断言
        with self.login.page.expect_navigation(url='**/index.html'):
            self.login.click_login_button()

    def test_login_ajax(self):
        """登录正常流程， 获取异步ajax 请求"""
        self.login.fill_username("py")
        self.login.fill_password('123456')
        # 捕获ajax请求
        with self.login.page.expect_request('**/api/login') as req:
            self.login.click_login_button()
        print(req.value)  # 获取请求对象
        print(req.value.method)  # 获取请求对象
        print(req.value.header_value)  # 获取请求对象
        print(req.value.post_data_json)  # 获取请求对象
        # 断言请求内容
        assert req.value.method == 'POST'
        assert req.value.header_value('content-type') == 'application/json'
        assert req.value.post_data_json == {'username': 'py', 'password': '123456'}

    def test_login_ajax_response(self):
        """登录正常流程， 获取异步ajax 响应"""
        self.login.fill_username("py")
        self.login.fill_password('123456')
        # 捕获ajax请求
        with self.login.page.expect_response('**/api/login') as res:
            self.login.click_login_button()
        print(res.value)  # 获取返回对象
        print(res.value.url)
        print(res.value.status)
        print(res.value.ok)
        # print(res.value.body()) # 重定向下个页面，获取不到
        assert res.value.ok
        assert res.value.status == 200

    def test_login_link(self):
        """已有账号？点这登录 链接访问"""
        expect(self.login.locator_register_link).to_have_attribute('href', 'register.html')
        # 点击
        self.login.click_register_link()
        expect(self.login.page).to_have_url('/register.html')
        expect(self.login.page).to_have_title('注册')
