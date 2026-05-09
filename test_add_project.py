from pages.add_project_page import AddProjectPage
from playwright.sync_api import expect, Page
import pytest
import uuid
from mocks import mock_api


class TestAddProject:
    """添加项目"""

    @pytest.fixture(autouse=True)
    def start_for_each(self, login_first, page: Page):
        print("for each--start: 打开添加项目页")
        self.add_project = AddProjectPage(page)
        self.add_project.navigate()
        yield
        print("for each--end: 后置操作")

    @pytest.mark.parametrize("name, app, desc", [
        ["abc!@", "", ""],
        ["aaaaabbbbbcccccdddddeeeeefffff1", "", ""],
        ["abc", "aa!@", ""]
    ])
    def test_add_project_disabled(self, name, app, desc):
        """异常场景-项目名称，无效等价：特殊字符/大于30个字符"""
        self.add_project.fill_project_name(name)
        self.add_project.fill_publish_app(app)
        self.add_project.fill_project_desc(desc)
        # 断言提交按钮状态 不可点击
        expect(self.add_project.locator_save_button).to_be_disabled()

    def test_add_project_null(self):
        """异常场景-项目名称不能为空"""
        self.add_project.fill_project_name("")
        self.add_project.fill_publish_app("")
        self.add_project.fill_project_desc("")
        self.add_project.click_save_button()
        # 断言提交按钮状态 不可点击
        expect(self.add_project.locator_save_button).to_be_disabled()

    def test_add_project_success(self, page: Page):
        """提交成功，跳转到项目列表"""
        # 生成随机账号
        self.add_project.fill_project_name(str(uuid.uuid4()).replace('-', '')[:25])
        self.add_project.fill_publish_app("xx")
        self.add_project.fill_project_desc("xxx")
        # 断言跳转到项目列表页
        with page.expect_navigation(url="**/list_project.html"):
            # 保存成功后，重定向到列表页
            self.add_project.click_save_button()

    def test_add_project_400(self, page: Page):
        """项目名称重复，弹出模态框"""
        self.add_project.fill_project_name("yo yo")
        self.add_project.fill_publish_app("xx")
        self.add_project.fill_project_desc("xxx")
        # mock 接口返回400
        page.route(**mock_api.mock_project_400)
        self.add_project.click_save_button()
        # 校验结果 弹出框文本包含
        expect(self.add_project.locator_boot_box).to_be_visible()
        expect(self.add_project.locator_boot_box).to_contain_text('已存在')

    def test_add_project_500(self, page: Page):
        """服务器异常 500 状态码"""
        self.add_project.fill_project_name("test")
        self.add_project.fill_publish_app("xx")
        self.add_project.fill_project_desc("xxx")
        # mock 接口返回500
        page.route(**mock_api.mock_project_500)
        self.add_project.click_save_button()
        # 校验结果 弹出框文本包含
        expect(self.add_project.locator_boot_box).to_contain_text('操作异常')

    def test_add_project_success2(self, page: Page):
        """提交成功，判断新项目名称在列表"""
        # 生成随机账号
        new_project_name = str(uuid.uuid4()).replace('-', '')[:25]
        self.add_project.fill_project_name(new_project_name)
        self.add_project.fill_publish_app("xx")
        self.add_project.fill_project_desc("xxx")
        # 保存成功后
        self.add_project.click_save_button()
        # 点击保存后等页面重定向到table表格页
        self.add_project.page.wait_for_load_state('networkidle')
        # 断言新增项目在列表页
        print(f"新增项目名称: {new_project_name}")
        # 获取页面 table 表格-项目名称列全部内容
        loc_projects = self.add_project.page.locator(
            '//table[@id="table"]//td[3]/a'
        )
        # 获取文本
        project_names = [i.inner_text() for i in loc_projects.all()]
        print(f"获取页面 table 表格-项目名称列全部内容: {project_names}")
        assert new_project_name in project_names
