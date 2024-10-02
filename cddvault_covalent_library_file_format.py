# cddvault_covalent_library+file_format.py
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw
import matplotlib.pyplot as plt
from datetime import datetime

def load_data(file1, file2):
    try:
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error: One of the input files was not found. Please check the file paths.\n{str(e)}")
    except pd.errors.EmptyDataError as e:
        raise ValueError(f"Error: One of the input files is empty. Please provide valid CSV files.\n{str(e)}")
    except Exception as e:
        raise Exception(f"An error occurred while loading the input files: {str(e)}")
    return df1, df2

def merge_data(df1, df2):
    required_columns_df1 = ["Container Id", "Orientation Barcode", "Row", "Column", "Barcode", "Scan Time"]
    required_columns_df2 = ["VIAL_QR_CODE", "SYNONYMS", "SMILES", "INITIAL_VOLUME_UL", "CONC_mM", "SALT"]
    
    missing_columns_df1 = [col for col in required_columns_df1 if col not in df1.columns]
    missing_columns_df2 = [col for col in required_columns_df2 if col not in df2.columns]
    
    if missing_columns_df1:
        raise ValueError(f"Error: Input file 1 is missing the following required columns: {missing_columns_df1}")
    if missing_columns_df2:
        raise ValueError(f"Error: Input file 2 is missing the following required columns: {missing_columns_df2}")
    
    try:
        merged_df = pd.merge(df1, df2, left_on="Barcode", right_on="VIAL_QR_CODE", how="outer", indicator=True)
        unmatched_df2 = merged_df[merged_df['_merge'] == 'right_only']
        if not unmatched_df2.empty:
            error_message = "Mismatch found: The following 'VIAL_QR_CODES' in File 2 did not match any 'Barcode' in File 1:\n"
            error_message += ', '.join(unmatched_df2['VIAL_QR_CODE'].astype(str).tolist())
            error_message += "\nPlease double check these 'VIAL_QR_CODE' values."
            raise ValueError(error_message)
        merged_df = merged_df[merged_df['_merge'] == 'both'].drop(columns=['_merge'])
    except Exception as e:
        raise Exception(f"An error occurred during merging: {str(e)}")
    
    merged_df["PLATE_WELL"] = merged_df["Row"].astype(str) + merged_df["Column"].astype(str)
    return merged_df

def visualize_smiles(merged_df):
    try:
        smiles_data = merged_df[['VIAL_QR_CODE', 'SYNONYMS', 'SMILES']].copy()
        smiles_data['Image'] = smiles_data['SMILES'].apply(lambda x: smiles_to_image(x))
        for index, row in smiles_data.iterrows():
            print(f"\nVIAL_QR_CODE: {row['VIAL_QR_CODE']}, SYNONYMS: {row['SYNONYMS']}, SMILES: {row['SMILES']}")
            plt.imshow(row['Image'])
            plt.xticks([])
            plt.yticks([])
            plt.title(f"VIAL_QR_CODE: {row['VIAL_QR_CODE']}")
            plt.show()
    except Exception as e:
        raise Exception(f"An error occurred while processing SMILES strings: {str(e)}")

def save_output(output_df):
    current_date = datetime.now().strftime("%Y%m%d")
    output_file_path = f"CDDupload_input_file_{current_date}.csv"
    try:
        output_df.to_csv(output_file_path, index=False)
        print(f"Output file saved to: {output_file_path}")
    except Exception as e:
        raise Exception(f"An error occurred while saving the output file: {str(e)}")

def main(input_file_1, input_file_2):
  df1, df2 = load_data(input_file_1, input_file_2)
  merged_df = merge_data(df1, df2)
  visualize_smiles(merged_df)
  save_output(merged_df)

If __name__ == '__main__':
  main(input_file_1, inputfile_2)
