import pandas as pd  
from .utils import get_csv_path, print_success, print_progress  
  
def validate_csv(filename: str, expected_min_rows: int = 1):  
    path = get_csv_path(filename)  
    if not path.exists():  
        raise FileNotFoundError(f'Missing {filename}')  
    df = pd.read_csv(path)  
    if len(df) < expected_min_rows:  
        raise ValueError(f'{filename} has {len(df)} rows, expected at least {expected_min_rows}')  
    return len(df) 
