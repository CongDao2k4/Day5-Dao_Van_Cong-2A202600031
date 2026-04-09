import os
from datetime import datetime
from typing import Any

import pandas as pd
from langchain_core.tools import tool


@tool
def export_data(
    data: list[dict[str, Any]] | pd.DataFrame,
    format: str = 'csv',
    filename_prefix: str = 'export',
) -> str:
    """Export rows to CSV or Excel under `./exports/`."""
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
        if format.lower() in ['excel', 'xlsx']:
            file_path = os.path.join(export_dir, f'{filename_prefix}_{timestamp}.xlsx')
            df.to_excel(file_path, index=False, engine='openpyxl')
        else:
            file_path = os.path.join(export_dir, f'{filename_prefix}_{timestamp}.csv')
            # BOM helps Excel on Windows open UTF-8 CSV with non-ASCII text.
            df.to_csv(file_path, index=False, encoding='utf-8-sig')

        return f'Exported successfully to: {file_path}'

    except Exception as e:
        return f'Export failed: {str(e)}'
