from pages.register_page import RegisterPage
from playwright.sync_api import expect, Page
import pytest
import uuid


class TestRegister:
    """注册功能"""

    @pytest.fixture(autouse=True)
    def start_for_each(self, unlogin_page: Page):
        """
        同登录功能用独立的上下文环境，不加载cookie
        :param unlogin_page: 独立上下文
        :return: None
        """
        print("for each--start: 打开新页面访问注册页")
        self.register = RegisterPage(unlogin_page)
        self.register.navigate()
        yield
        print("for each--end: 后置操作")

    def test_register_1(self):
        """用户名为空，点注册"""
        self.register.fill_username('')
        self.register.fill_password('123456')
        self.register.click_register_button()
        # 断言
        expect(self.register.locator_username_tip1).to_be_visible()
        expect(self.register.locator_username_tip1).to_contain_text("不能为空")

    def test_register_2(self):
        """用户名大于30字符"""
        self.register.fill_username('hello world hello world hello world')
        # 断言
        expect(self.register.locator_username_tip2).to_be_visible()
        expect(self.register.locator_username_tip2).to_contain_text("用户名称1-30位字符")
        # 断言 注册按钮不可点击
        expect(self.register.locator_register_btn).not_to_be_enabled()

    def test_register_3(self):
        """用户名有特殊字符"""
        self.register.fill_username('hello!@#')
        # 断言
        expect(self.register.locator_username_tip3).to_be_visible()
        expect(self.register.locator_username_tip3).to_contain_text("用户名称不能有特殊字符,请用中英文数字")
        # 断言 注册按钮不可点击
        expect(self.register.locator_register_btn).not_to_be_enabled()

    def test_register_4(self):
        """密码框不能为空"""
        self.register.fill_username('hello')
        self.register.fill_password('')
        self.register.click_register_button()
        # 断言
        expect(self.register.locator_password_tip1).to_be_visible()
        expect(self.register.locator_password_tip1).to_contain_text("不能为空")

    @pytest.mark.parametrize('test_input', ['abc12', 'abc1234567890abc1'])
    def test_register_5(self, test_input):
        """密码框6-16位"""
        self.register.fill_password(test_input)
        # 断言
        expect(self.register.locator_password_tip2).to_be_visible()
        expect(self.register.locator_password_tip2).to_contain_text("密码6-16位字符")

    def test_register_6(self):
        """密码框不能有特殊字符"""
        self.register.fill_password('abc123!')
        # 断言
        expect(self.register.locator_password_tip3).to_be_visible()
        expect(self.register.locator_password_tip3).to_contain_text("不能有特殊字符,请用中英文数字下划线")

    def test_login_link(self):
        """已有账号？点这登录"""
        expect(self.register.locator_login_link).to_have_attribute("href", "login.html")
        self.register.click_login_link()
        expect(self.register.page).to_have_title('网站登录')

    def test_register_error(self):
        """测试注册正常流程，已被注册过的账号"""
        self.register.fill_username('py')
        self.register.fill_password('123456')
        self.register.click_register_button()
        # 断言提示语可见
        expect(self.register.locator_register_error).to_be_visible()

    def test_register_success(self):
        """测试注册正常流程，注册成功"""
        self.register.fill_username(str(uuid.uuid4())[:8])
        self.register.fill_password('aa123456')
        self.register.click_register_button()
        expect(self.register.page).to_have_title("首页")
        expect(self.register.page).to_have_url("/index.html")
