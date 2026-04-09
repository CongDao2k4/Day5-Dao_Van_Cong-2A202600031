import os
from datetime import datetime
from typing import Any, Dict, List, Union

import pandas as pd
from langchain_core.tools import tool

from src.telemetry.logger import logger


@tool
def export_data(
    data: Union[List[Dict[str, Any]], pd.DataFrame],
    format: str = 'csv',
    filename_prefix: str = 'export',
) -> str:
    """
    Converts query results into CSV or Excel format.

    Args:
        data: The data to be exported; can be a pandas DataFrame or a list of dictionaries (rows).
        format: The desired output format ('csv' or 'excel'). Defaults to 'csv'.
        filename_prefix: The prefix for the generated filename.

    Returns:
        str: A success message containing the file path, or an error message.
    """
    if isinstance(data, list):
        if not data:
            return 'No data to export'
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        if data.empty:
            return 'No data to export'
        df = data
    else:
        return 'Invalid data format. Expected List[Dict] or DataFrame.'

    export_dir = 'exports'
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    try:
        # 3. Xử lý xuất file
        if format.lower() in ['excel', 'xlsx']:
            file_path = os.path.join(export_dir, f'{filename_prefix}_{timestamp}.xlsx')
            df.to_excel(file_path, index=False, engine='openpyxl')
        else:
            file_path = os.path.join(export_dir, f'{filename_prefix}_{timestamp}.csv')
            # utf-8-sig giúp Excel trên Windows đọc được tiếng Việt (mssv, tên sinh viên)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')

        return f'Exported successfully to: {file_path}'

    except Exception as e:
        return f'Export failed: {str(e)}'


if __name__ == '__main__':
    mock_data = [
        {
            'mssv': '2A202600020',
            'full_name': 'Đặng Hồ Hải',
            'major': 'AI Engineer',
            'status': 'active',
        },
        {
            'mssv': '2A202600999',
            'full_name': 'Nguyen Van A',
            'major': 'Computer Science',
            'status': 'leave',
        },
    ]

    print('\n[Test 1] Export CSV...')
    result_csv = export_data.invoke(
        {'data': mock_data, 'format': 'csv', 'filename_prefix': 'test_student_report'}
    )
    print(result_csv)

    print('\n[Test 2] Export Excel...')
    result_excel = export_data.invoke(
        {'data': mock_data, 'format': 'excel', 'filename_prefix': 'test_student_report'}
    )
    print(result_excel)
