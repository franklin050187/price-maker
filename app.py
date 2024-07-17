"""user interface for price maker"""
import streamlit as st
from filegen import convert_input_to_output, export_to_excel


# Define the gen function
def gen(file):
    """
    A function that takes a file, reads its content, converts the input to output using 
    the convert_input_to_output function, then prints and returns the data.

    Parameters:
    - file: the file object to be processed

    Returns:
    - data: the processed output data
    """
    data = convert_input_to_output(file)
    # print(data)
    return data


# Create the Streamlit app
def main():
    """
    A function to manage the main functionality of the app including file upload,
    processing, and user interactions.
    """
    st.title("File Upload and Processing App \n Last date is excluded : \n 2022-12-01 to 2022-12-31 is 31 lines")

    # File uploader
    uploaded_file = st.file_uploader(
        label="Upload a file",
        type=["xlsx"],
        key="file_uploader",
        help="Must have columns iddetail, prixperiode, datedebut, datefin",
        disabled=False,
    )

    if uploaded_file is not None:
        # Call the gen function with the uploaded file
        result = gen(uploaded_file)

        # Display the result
        st.write("Preview :")
        st.text(result)

        # add radio button
        option = st.radio(
            "Select an option",
            ("1 file", "1 file per id detail", "1 file per 1000 lines"),
            index=None,
            key="option_radio",
            help="Please select an option",
            disabled=False,
        )
        if option is None:
            st.error("Please select an option")
        elif option == "1 file":
            # get the whole file
            for name, result_file in export_to_excel(result, group_type=option):
                # print("result option 1", result_file)
                # print("name option 1", name)
                st.download_button(label="Download file", data=result_file, file_name=name)
        elif option == "1 file per id detail":
            for name, result_file in export_to_excel(result, group_type=option):
                # print("result option 2", result_file)
                # print("name option 2", name)
                st.download_button(label="Download file", data=result_file, file_name=name)
        elif option == "1 file per 1000 lines":
            for name, result_file in export_to_excel(result, group_type=option):
                # print("result option 2", result_file)
                # print("name option 2", name)
                st.download_button(label="Download file", data=result_file, file_name=name)


if __name__ == "__main__":
    main()
