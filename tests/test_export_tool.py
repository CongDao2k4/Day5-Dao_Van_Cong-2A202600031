import os

import pandas as pd
import pytest

from tools.export_data_tool import export_data


@pytest.fixture
def mock_data():
    return [
        {'mssv': '2A202600020', 'full_name': 'Đặng Hồ Hải', 'status': 'active'},
        {'mssv': '2A202600999', 'full_name': 'Nguyen Van A', 'status': 'leave'},
    ]


# Test trường hợp xuất CSV thành công
def test_export_csv_success(mock_data):
    prefix = 'test_csv'
    result = export_data.invoke(
        {'data': mock_data, 'format': 'csv', 'filename_prefix': prefix}
    )

    assert 'successfully' in result
    # Kiểm tra file có thực sự tồn tại trong thư mục exports/
    files = [
        f for f in os.listdir('exports') if f.startswith(prefix) and f.endswith('.csv')
    ]
    assert len(files) > 0

    df = pd.read_csv(os.path.join('exports', files[0]), encoding='utf-8-sig')
    assert len(df) == 2
    assert df.iloc[0]['full_name'] == 'Đặng Hồ Hải'


# Test trường hợp xuất Excel thành công
def test_export_excel_success(mock_data):
    prefix = 'test_excel'
    result = export_data.invoke(
        {'data': mock_data, 'format': 'excel', 'filename_prefix': prefix}
    )

    assert 'successfully' in result
    files = [
        f for f in os.listdir('exports') if f.startswith(prefix) and f.endswith('.xlsx')
    ]
    assert len(files) > 0


# Test trường hợp dữ liệu rỗng
def test_export_empty_data():
    result = export_data.invoke({'data': [], 'format': 'csv'})
    assert 'Không có dữ liệu' in result or 'No data' in result


# Test định dạng không hợp lệ (ví dụ: pdf)
def test_export_default_to_csv_on_invalid_format(mock_data):
    prefix = 'test_invalid'
    result = export_data.invoke(
        {'data': mock_data, 'format': 'pdf', 'filename_prefix': prefix}
    )
    assert '.csv' in result
