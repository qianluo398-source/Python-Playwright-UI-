import os
import pytest

if __name__ == '__main__':
    # 运行测试用例
    pytest.main(['--alluredir', './reports'])
    # 生成测试报告
    os.system('allure generate ./reports -o ./allure_report --clean')
    # 打开测试报告
    # os.system('allure serve ./reports')
