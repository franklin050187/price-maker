"""file generator"""

import io
import zipfile

import pandas as pd


def create_import_file(price, iddetail, startdate, enddate):
    """
    Creates an import file for a given price, iddetail, startdate, and enddate.

    Args:
        price (float): The price for each day.
        iddetail (int): The id detail for each line.
        startdate (str): The start date in '%Y-%m-%d' format.
        enddate (str): The end date in '%Y-%m-%d' format.

    Returns:
        pandas.DataFrame: A DataFrame with the following columns:
            - 'Id detail' (int): The id detail for each line.
            - 'Date' (datetime): The date for each line.
            - 'Tarif' (float): The price for each line.
            - 'Actif' (str): The status of each line.
            - 'Durée min' (str): The minimum duration for each line.
            - 'Durée max' (str): The maximum duration for each line.
            - 'Arrivée autorisée' (str): The status of arrival for each line.
    """
    # create table with headers Id detail	Date	Tarif	Actif	Durée min	Durée max	Arrivée autorisée
    df_if = pd.DataFrame(
        columns=[
            "Id detail",
            "Date",
            "Tarif",
            "Actif",
            "Durée min",
            "Durée max",
            "Arrivée autorisée",
        ]
    )
    # count number of days between startdate and enddate
    days = (pd.to_datetime(enddate) - pd.to_datetime(startdate)).days
    price_per_day = price / days
    price_rounded = round(price_per_day, 2)
    diff = price_rounded * days - price
    diff_rounded = round(diff, 2)
    # ensure sum of price per day is equal to price for the period
    lastdayprice = price_rounded - diff_rounded
    # diff_check = price_rounded * (days - 1) + lastdayprice - price # should confirm total price
    # for each day insert a line
    for i in range(days):
        date = pd.to_datetime(startdate) + pd.Timedelta(days=i)
        new_row = pd.DataFrame(
            {
                "Id detail": [iddetail],
                "Date": [date],
                "Tarif": [price_rounded],
                "Actif": ["VRAI"],
                "Durée min": [""],
                "Durée max": [""],
                "Arrivée autorisée": ["VRAI"],
            }
        )

        # remove empty row and columns before concat
        new_row = new_row.dropna(axis=1, how="all").dropna(how="all")
        df_if = pd.concat(
            [df_if.dropna(axis=1, how="all").dropna(how="all"), new_row], ignore_index=True
        )
        if i == days - 1:
            df_if.at[i, "Tarif"] = lastdayprice
    return df_if


# save df to xlsx file
def export_to_excel(df, group_type):
    """converts df to xlsx, returns BytesIO"""
    if group_type == "1 file":
        # print("1 file")
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False)  # write to BytesIO buffer
        towrite.seek(0)
        filename = "output_all.xlsx"
        # print(filename)
        yield filename, towrite
    elif group_type == "1 file per id detail":
        # print("1 file per id detail")
        files_to_zip = []
        df_grouped = df.groupby("Id detail")
        for name, group in df_grouped:
            filename = str(name) + ".xlsx"
            towrite = io.BytesIO()
            group.to_excel(towrite, index=False)  # write to BytesIO buffer
            towrite.seek(0)
            # print(filename)
            files_to_zip.append((filename, towrite))
        # store all files in a zip
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, file_buffer in files_to_zip:
                zip_file.writestr(filename, file_buffer.getvalue())
        zip_buffer.seek(0)
        yield "files_by_id.zip", zip_buffer
    elif group_type == "1 file per 1000 lines":
        # print("1 file per 1000 lines")
        files_to_zip = []
        # split per 1000 lines
        df_1000 = [df.iloc[i : i + 1000] for i in range(0, len(df), 1000)]
        # for every 1000 lines create a file
        for i, group in enumerate(df_1000):
            filename = f"output_{i}.xlsx"
            towrite = io.BytesIO()
            group.to_excel(towrite, index=False)  # write to BytesIO buffer
            towrite.seek(0)
            # print(filename)
            files_to_zip.append((filename, towrite))
        # store all files in a zip
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, file_buffer in files_to_zip:
                zip_file.writestr(filename, file_buffer.getvalue())
        zip_buffer.seek(0)
        yield "files_by_1000.zip", zip_buffer


def convert_input_to_output(input_file):
    """
    A function that converts an input Excel file to a final DataFrame after processing each line.

    Parameters:
    - input: the path to the input Excel file
    - columns required: ["iddetail", "prixperiode", "datedebut", "datefin"]

    Returns:
    - final_df: a single DataFrame containing the processed data from the input file
    """
    # import excel file
    dfinput = pd.read_excel(input_file)

    # check required columns
    required_columns = ["iddetail", "prixperiode", "datedebut", "datefin"]
    missing_columns = set(required_columns) - set(dfinput.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # create a recipient
    all_dfs = []

    # pass the data to the create_import_file function for each line in the file
    for _, line in dfinput.iterrows():
        iddetail = line["iddetail"]
        price = line["prixperiode"]
        startdate = line["datedebut"]
        enddate = line["datefin"]
        linedf = create_import_file(
            price=price, iddetail=iddetail, startdate=startdate, enddate=enddate
        )
        # Append the DataFrame to the list
        all_dfs.append(linedf)

    # Concatenate all DataFrames in the list into a single DataFrame
    final_df = pd.concat(all_dfs, ignore_index=True)
    return final_df
