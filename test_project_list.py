import pytest
from pages.project_list_page import ProjectListPage, Page
from playwright.sync_api import expect
from mocks import mock_api


class TestProjectList:
    """项目列表"""

    @pytest.fixture(autouse=True)
    def start_for_each(self, login_first, page: Page):
        print("for each--start: 打开项目列表页")
        self.project = ProjectListPage(page)
        self.project.navigate()
        yield
        print("for each--end: 后置操作")

    def test_add_project_null(self):
        """新增项目：项目名称为空"""
        self.project.click_add_project()
        self.project.locator_modal_project_name.fill('')
        self.project.locator_modal_save.click()
        # 断言模态框不隐藏
        expect(self.project.locator_add_modal).not_to_be_hidden()

    def test_add_project_dismiss_btn(self):
        """新增项目：模态框取消按钮"""
        self.project.click_add_project()
        self.project.locator_modal_project_name.fill('')
        self.project.locator_modal_dismiss.click()
        # 断言模态框隐藏
        expect(self.project.locator_add_modal).not_to_be_visible()

    def test_add_project_400(self):
        """新增项目：项目名称重复，状态码400"""
        self.project.click_add_project()
        self.project.locator_modal_project_name.fill('yo yo')
        # mock 接口返回400
        self.project.page.route(**mock_api.mock_project_400)
        self.project.locator_modal_save.click()
        # 断言模态框提示语
        expect(self.project.page.locator('.bootbox-body')).to_contain_text('已存在')

    def test_add_project_500(self):
        """新增项目：服务器异常状态码500"""
        self.project.click_add_project()
        self.project.locator_modal_project_name.fill('yo yo')
        # mock 接口返回500
        self.project.page.route(**mock_api.mock_project_500)
        self.project.locator_modal_save.click()
        # 断言模态框提示语
        expect(self.project.page.locator('.bootbox-body')).to_contain_text('操作异常')

    def test_add_project_success(self):
        """新增项目成功，跳转到列表页"""
        self.project.click_add_project()
        self.project.locator_modal_project_name.fill('yo yo')
        # mock 接口返回200
        self.project.page.route(**mock_api.mock_project_200)
        self.project.locator_modal_save.click()
        # 断言模态框隐藏，并且重定向到列表页
        expect(self.project.locator_add_modal).not_to_be_visible()

    def test_search_project_ajax(self):
        """项目列表搜索功能，点搜索按钮查询请求"""
        self.project.search_project("test")
        # 点搜索按钮
        with self.project.page.expect_request('**/api/project**') as req:
            self.project.click_search_button()
        # 断言搜索请求参数
        assert "project_name=test" in req.value.url
        assert req.value.method == "GET"

    def test_search_project_0(self):
        """项目列表页搜索功能， 模拟搜索0个结果"""
        self.project.search_project("test")
        # 期望输入框有内容
        expect(self.project.locator_search_project).to_have_value('test')
        # 点搜索按钮
        self.project.page.route(**mock_api.mock_project_search_0)
        self.project.click_search_button()
        # 期望结果 值搜索一个值
        expect(self.project.locator_table_tr).to_contain_text('没有找到匹配的记录')

    def test_search_project_1(self):
        """项目列表页搜索功能， 模拟搜索一个结果"""
        self.project.search_project("test")
        # 期望输入框有内容
        expect(self.project.locator_search_project).to_have_value('test')
        # 点搜索按钮
        self.project.page.route(**mock_api.mock_project_search_1)
        self.project.click_search_button()
        # 期望结果 值搜索一个值
        expect(self.project.locator_table_tr).to_have_count(1)

    def test_refresh_project_ajax(self):
        """项目列表刷新功能，点刷新按钮查询请求"""
        with self.project.page.expect_request('**/api/project**') as req:
            self.project.click_refresh()
        print(req.value.url)
        assert "page=1&size=15&project_name=&" in req.value.url
        assert req.value.method == "GET"

    def test_table_link(self):
        """表格行内 链接"""
        # 造数据，mock 行内数据
        self.project.page.route(**mock_api.mock_project_search_1)
        # 重新刷新页面
        self.project.page.reload()
        # 断言
        expect(self.project.locator_link_debugtalk).to_have_attribute("href", "debugtalk.html?project_id=1")

    def test_table_delete(self):
        """表格行内删除 {"message": "无权限操作，请联系管理员"}"""
        # 造数据，mock 行内数据
        self.project.page.route(**mock_api.mock_project_search_1)
        # 重新刷新页面
        self.project.page.reload()
        # 点删除
        self.project.locator_table_delete.click()
        expect(self.project.locator_boot_box).to_contain_text('确定要删除选中的数据？')
        # mock 拦截请求，返回{"message": "无权限操作，请联系管理员"}
        self.project.page.route(**mock_api.mock_project_delete_403)
        # 点确定删除
        self.project.locator_boot_box_accept.click()
        # 有个boot_box，获取最后一个
        expect(self.project.locator_boot_box.last).to_contain_text('操作异常："无权限操作，请联系管理员"')

    def test_table_edit(self):
        """表格行内编辑"""
        # 造数据，mock 行内数据
        self.project.page.route(**mock_api.mock_project_search_1)
        # 重新刷新页面
        self.project.page.reload()
        self.project.locator_table_edit.first.click()
        # 断言
        expect(self.project.locator_edit_modal).to_be_visible()
