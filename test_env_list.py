import pytest
from pages.list_env_page import EnvListPage, Page
from playwright.sync_api import expect
from mocks import mock_api


class TestEnvList:
    """环境列表"""

    @pytest.fixture(autouse=True)
    def start_for_each(self, login_first, page: Page):
        print("for each--start: 打开项目列表页")
        self.env = EnvListPage(page)
        self.env.navigate()
        yield
        print("for each--end: 后置操作")

    def test_add_env_name_null(self):
        """新增环境：环境名称不能为空"""
        self.env.click_add_env()  # 弹出新增框
        # 断言模态框不隐藏
        expect(self.env.locator_add_modal).not_to_be_hidden()
        self.env.input_env_name('')
        self.env.click_modal_save()
        # 断言不能为空
        expect(self.env.locator_modal_env_tip1).to_be_visible()
        expect(self.env.locator_modal_env_tip1).to_have_text('不能为空')

    def test_add_env_name_long(self):
        """新增环境：大于30个字符"""
        self.env.click_add_env()  # 弹出新增框
        # 断言模态框不隐藏
        expect(self.env.locator_add_modal).not_to_be_hidden()
        self.env.input_env_name('hello world hello world hello world hello world')
        self.env.click_modal_save()
        # 断言不能为空
        expect(self.env.locator_modal_env_tip2).to_be_visible()
        expect(self.env.locator_modal_env_tip2).to_have_text('模块名称1-40位字符')

    @pytest.mark.parametrize("name", ["abc!@", "$32", "\\xx"])
    def test_add_env_name_invalid(self, name):
        """新增环境：不能有特殊字符"""
        self.env.click_add_env()  # 弹出新增框
        # 断言模态框不隐藏
        expect(self.env.locator_add_modal).not_to_be_hidden()
        self.env.input_env_name(name)
        self.env.click_modal_save()
        # 断言不能为空
        expect(self.env.locator_modal_env_tip3).to_be_visible()
        expect(self.env.locator_modal_env_tip3).to_have_text('模块名称不能有特殊字符')

    def test_add_env_address_null(self):
        """新增环境：环境地址不能为空"""
        self.env.click_add_env()  # 弹出新增框
        # 断言模态框不隐藏
        expect(self.env.locator_add_modal).not_to_be_hidden()
        self.env.input_env_name('env')
        self.env.input_env_address('')
        self.env.click_modal_save()
        # 断言不能为空
        expect(self.env.locator_modal_address_tip1).to_be_visible()
        expect(self.env.locator_modal_address_tip1).to_have_text('不能为空')

    @pytest.mark.parametrize("address", ["abchttp", "httpx:", "httpsx://"])
    def test_add_env_address_invalid(self, address):
        """新增环境：环境地址必须以http:或 https:开头"""
        self.env.click_add_env()  # 弹出新增框
        # 断言模态框不隐藏
        expect(self.env.locator_add_modal).not_to_be_hidden()
        self.env.input_env_name('env')
        self.env.input_env_address(address)
        self.env.click_modal_save()
        # 断言不能为空
        expect(self.env.locator_boot_box).to_be_visible()
        expect(self.env.locator_boot_box).to_have_text('操作异常：{"base_url":"base_url must start with http:// or https://"}')

    def test_add_env_dismiss(self):
        """新增环境：点取消按钮"""
        self.env.click_add_env()  # 弹出新增框
        # 断言模态框不隐藏
        expect(self.env.locator_add_modal).not_to_be_hidden()
        self.env.input_env_name('')
        self.env.click_modal_dismiss()  # 取消按钮
        # 断言模态框不显示
        expect(self.env.locator_add_modal).not_to_be_visible()

    def test_add_env_exists(self):
        """新增环境：环境名称已存在"""
        self.env.click_add_env()  # 弹出新增框
        # 断言模态框不隐藏
        expect(self.env.locator_add_modal).not_to_be_hidden()
        self.env.input_env_name('py1')
        self.env.input_env_address('http://www.yoyo.com')
        # mock 返回400 已存在
        self.env.page.route(**mock_api.mock_add_env_400)
        self.env.click_modal_save()
        # 断言已存在
        expect(self.env.locator_boot_box).to_be_visible()
        expect(self.env.locator_boot_box).to_have_text('操作异常：{"env_name":"env_name: py1 已存在"}')

    def test_add_env_success(self):
        """新增环境：环境新增成功"""
        self.env.click_add_env()  # 弹出新增框
        # 断言模态框不隐藏
        expect(self.env.locator_add_modal).not_to_be_hidden()
        self.env.input_env_name('py2')
        self.env.input_env_address('http://www.yoyo.com')
        # mock 返回200 成功
        self.env.page.route(**mock_api.mock_add_env_200)
        self.env.click_modal_save()
        # 断言添加成功
        expect(self.env.locator_add_modal).not_to_be_visible()
