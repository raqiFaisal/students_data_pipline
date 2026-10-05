import pandas as pd


def write_csv(data: pd.DataFrame, file_path: str) -> None:
    """Write the final dataset to a CSV file."""
    data.to_csv(file_path, index=False)