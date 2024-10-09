import pandas as pd
import os

def merge_excel_spreadsheets(file1_path, file2_path, output_path='product_discounts.xlsx'):
    # Read both input Excel files
    df1 = pd.read_excel(file1_path)
    df2 = pd.read_excel(file2_path)

    # Concatenate the dataframes and remove duplicates
    merged_df = pd.concat([df1, df2]).drop_duplicates()

    # Sort the dataframe by discount_rate in descending order
    merged_df = merged_df.sort_values('discount_rate', ascending=False)

    # Check if the output file already exists
    if os.path.exists(output_path):
        # Read the existing file
        existing_df = pd.read_excel(output_path)

        # Find differences
        differences = pd.concat([existing_df, merged_df]).drop_duplicates(keep=False)

        if not differences.empty:
            # Save differences to a new file
            differences_path = 'differences.xlsx'
            differences.to_excel(differences_path, index=False)
            print(f"Differences saved as {differences_path}")
        else:
            print("No differences found.")

    # Save the merged result to the output file
    merged_df.to_excel(output_path, index=False)
    print(f"Merged spreadsheet saved as {output_path}")

