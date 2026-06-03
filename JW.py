import streamlit.web.cli as stcli
import streamlit as st
import pandas as pd
from clean_data import clean_data
from grp_sum import inv_sum
from io import BytesIO

# ---------------- PAGE SETUP ----------------
def setup_page():
    st.set_page_config(
        page_title="Job Work Data Module",
        page_icon=":bar_chart:",
        layout="wide"
    )

# ---------------- INPUT ----------------
def get_sheet_name():
    return st.sidebar.text_input("Please input the sheet name")

def file_upload():
    return st.sidebar.file_uploader("Choose a job Work Data file", type=('xls','xlsx'))

def mst_upload():
    return st.sidebar.file_uploader("Choose a Master Data file", type=('xls','xlsx'))

def get_a1_cell(df):
    #return df.iloc[0,0]
    return (df.columns[0])



def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

def main():

    setup_page()
    st.title("Job Work Data")
    
    # Master File Upload
    mst = mst_upload()
    file = file_upload()
    
    if mst is not None:
        try:
            df_mst = pd.read_excel(mst, sheet_name="Mst")
            df_dsgctg = pd.read_excel(mst, sheet_name="degctg")
            df_con = pd.read_excel(mst, sheet_name="con")
            
            #Display Master Data
            #st.subheader("Master")
            #st.dataframe(df_mst,use_container_width=True )
            #st.dataframe(df_dsgctg,use_container_width=True )
        except Exception as e:
            st.error(f"Error: {e}")

    # Job Work File Upload
    sheet = get_sheet_name()
    
    if not sheet:
        st.sidebar.error("Sheet name is manadtory")
        return
     
    if file is not None:
        try:
            df = pd.read_excel(file,sheet_name=sheet)
            #Display Jobwork Data
          
            #show the A1 Cell Value
            a1_cell = get_a1_cell(df)
            st.write(f":red[Export Ref : {a1_cell}]")
                        
            #clean the Data
            df_clean = clean_data(df,df_mst,df_dsgctg=df_dsgctg,df_con=df_con)
            st.dataframe(df_clean,use_container_width=True)
            
             # ---------------- SUMMARY ----------------
            df_sum = inv_sum(df_clean)

            st.subheader("Summary")
            st.dataframe(df_sum, use_container_width=True)
           
         
            #Excel download Button
            excel_data = to_excel(df_sum)
            
            st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name="Job_Work_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Error:{e}") 
            
        
        
# ---------------- RUN ----------------
if __name__ == "__main__":
    main()
