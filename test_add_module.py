from pages.add_module_page import AddModulePage
from playwright.sync_api import expect, Page
import pytest
from mocks import mock_api


class TestAddModule:
    """添加模块"""

    @pytest.fixture(autouse=True)
    def start_for_each(self, login_first, page: Page):
        print("for each--start: 打开添加模块页")
        self.add_module = AddModulePage(page)
        # 拦截项目选项数据，模拟返回选项
        self.add_module.page.route(**mock_api.mock_project_select_200)
        self.add_module.navigate()
        yield
        print("for each--end: 后置操作")

    def test_add_module_name_null(self):
        """添加模块-模块名称不能为空"""
        self.add_module.fill_module_name("")
        self.add_module.click_save_module()
        # 断言
        expect(self.add_module.locator_save_button).to_be_disabled()

    def test_add_module_project_null(self):
        """添加模块-项目名称不能为空"""
        self.add_module.fill_module_name("test")
        self.add_module.click_save_module()
        # 断言
        expect(self.add_module.locator_save_button).to_be_disabled()

    def test_add_module_repeat(self):
        """添加模块-模块名称重复"""
        self.add_module.fill_module_name("test")
        self.add_module.select_module_by_value("test")
        self.add_module.fill_module_desc("xxx")
        # mock 400数据
        self.add_module.page.route(**mock_api.mock_add_module_400)
        self.add_module.click_save_module()
        expect(self.add_module.locator_boot_box).to_contain_text('已存在')

    def test_add_module_success(self):
        """添加模块-模块名称添加成功"""
        self.add_module.fill_module_name("testx")
        self.add_module.select_module_by_value("test")
        self.add_module.fill_module_desc("xxx")
        # mock 200 成功数据
        self.add_module.page.route(**mock_api.mock_add_module_200)

        # 断言跳转到项目列表页
        with self.add_module.page.expect_navigation(url="**/list_module.html"):
            # 保存成功后，重定向到列表页
            self.add_module.click_save_module()
