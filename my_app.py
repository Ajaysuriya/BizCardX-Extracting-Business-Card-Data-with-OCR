
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3

def image_to_text(path):
    image_1= Image.open(path)

    #converting image to array format
    image_1_arr= np.array(image_1)

    reader = easyocr.Reader(['en'])

    text= reader.readtext(image_1_arr, detail= 0)

    return text, image_1

def extracted_text(texts):

  extracted_dict={"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[], "EMAIL":[], "WEBSITE":[],
                  "ADDRESS":[], "PINCODE":[]}

  extracted_dict["NAME"].append(texts[0])
  extracted_dict["DESIGNATION"].append(texts[1])

  for i in range(2,len(texts)):

    if texts[i].startswith("+") or (texts[i].replace("-","").isdigit()and '-' in texts[i]):

      extracted_dict["CONTACT"].append(texts[i])

    elif "@" in texts[i] and ".com" in texts[i]:

      extracted_dict["EMAIL"].append(texts[i])

    elif "WWW" in texts[i] or "WWW" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      small= texts[i].lower()

      extracted_dict["WEBSITE"].append(small)

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():

      extracted_dict["PINCODE"].append(texts[i])

    elif re.match(r'^[A-Za-z]', texts[i]):

      extracted_dict["COMPANY_NAME"].append(texts[i])

    else:
      remove_colon= re.sub(r'[,;]','',texts[i])

      extracted_dict["ADDRESS"].append(remove_colon)

  for key,value in extracted_dict.items():
    if len(value)>0:
      concadenate= " ".join(value)
      extracted_dict[key] = [concadenate]

    else:
      value= "NA"
      extracted_dict [key]= [value]

  return extracted_dict



#streamlit part

st.set_page_config(layout = "wide")
st.title("BizCardX: Extracting Business Card Data with OCR")

with st.sidebar:
  select= option_menu("Main Menu", ["Home", "Upload & Modifying", "Delete"])

if select == "Home":
  st.markdown("### :blue[**Technologies Utilized :**] Python,easy OCR, Streamlit, SQL, Pandas")



  st.write("### :green[**Overview :**] Bizcard is an application developed in Python, aimed at streamlining the process of information extraction from business cards.")
  st.write('### The primary objective of Bizcard is to automate the extraction of essential details from business card images. This includes information such as the individual’s name, their designation, the company they represent, contact details, and other pertinent data. Bizcard harnesses the capabilities of Optical Character Recognition (OCR) via EasyOCR to effectively extract text from these images. This automation facilitates a more efficient and accurate data extraction process.')

elif select == "Upload & Modifying":
  img = st.file_uploader("Upload the Image", type = ["png", "jpg", "jpeg"])

  if img is not None:
    st.image(img, width= 300)

    text_img, image_1 = image_to_text(img)

    text_dict= extracted_text(text_img)

    if text_dict:
      st.success("TEXT IS EXTRACTED SUCCESSFULLY")

    df= pd.DataFrame(text_dict)

    #Converting Image to Bytes

    Img_bytes = io.BytesIO()
    image_1.save(Img_bytes, format= "PNG")

    img_data = Img_bytes.getvalue()

    #Creating Dictionary

    data = {"IMAGE":[img_data]}

    df_1 = pd.DataFrame(data)

    concat_df = pd.concat([df,df_1],axis= 1)

    st.dataframe(concat_df)

    Button_1 = st.button("save", use_container_width= True)

    if Button_1:

      mydb = sqlite3.connect("Bizcard.db")
      mycursor = mydb.cursor()

      #Table creation

      create_table_query = '''CREATE TABLE IF NOT EXISTS Bizcard_details(NAME varchar(225),
                              DESIGNATION varchar(225),
                              COMPANY_NAME varchar(225),
                              CONTACT varchar(225),
                              EMAIL varchar(225),
                              WEBSITE text,
                              ADDRESS text,
                              PINCODE varchar(225),
                              IMAGE text
                              ) '''

      mycursor.execute(create_table_query)
      mydb.commit()

      # Insert query

      insert_query = '''INSERT INTO Bizcard_details(NAME,
                        DESIGNATION,
                        COMPANY_NAME,
                        CONTACT,
                        EMAIL,
                        WEBSITE,
                        ADDRESS,
                        PINCODE,
                        IMAGE
                        )

                        values(?,?,?,?,?,?,?,?,?)'''

      datas = concat_df.values.tolist()[0]

      mycursor.execute(insert_query, datas)
      mydb.commit()

      st.success("SAVED SUCCESSFULLY")

  method = st.radio("Select th Method", ["None","Preview","Modify"])

  if method == "None":
    st.write("")

  if method == "Preview":

    mydb = sqlite3.connect("Bizcard.db")
    mycursor = mydb.cursor()

    #Select query
    select_query = "SELECT * FROM Bizcard_details"

    mycursor.execute(select_query)
    table = mycursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table, columns = ("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"))
    st.dataframe(table_df)

  elif method == "Modify":

    mydb = sqlite3.connect("Bizcard.db")
    mycursor = mydb.cursor()

    #Select query
    select_query = "SELECT * FROM Bizcard_details"

    mycursor.execute(select_query)
    table = mycursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table, columns = ("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"))

    col1,col2 = st.columns(2)

    with col1:

      Select_name = st.selectbox("Select the name", table_df["NAME"])

    df_3 = table_df[table_df["NAME"] == Select_name]

    df_4 = df_3.copy()

    col1,col2 = st.columns(2)

    with col1:

      modify_name = st.text_input("NAME", df_3["NAME"].unique()[0])
      modify_designation = st.text_input("DESIGNATION", df_3["DESIGNATION"].unique()[0])
      modify_company_name = st.text_input("COMPANY_NAME", df_3["COMPANY_NAME"].unique()[0])
      modify_contact = st.text_input("CONTACT", df_3["CONTACT"].unique()[0])
      modify_Email = st.text_input("EMAIL", df_3["EMAIL"].unique()[0])

      df_4["NAME"] = modify_name
      df_4["DESIGNATION"] = modify_designation
      df_4["COMPANY_NAME"] = modify_company_name
      df_4["CONTACT"] = modify_contact
      df_4["EMAIL"] = modify_Email

    with col2:

      modify_website = st.text_input("WEBSITE", df_3["WEBSITE"].unique()[0])
      modify_address = st.text_input("ADDRESS", df_3["ADDRESS"].unique()[0])
      modify_pincode = st.text_input("PINCODE", df_3["PINCODE"].unique()[0])
      modify_image = st.text_input("IMAGE", df_3["IMAGE"].unique()[0])

      df_4["WEBSITE"] = modify_website
      df_4["ADDRESS"] = modify_address
      df_4["PINCODE"] = modify_pincode
      df_4["IMAGE"] = modify_image

    st.dataframe(df_4)

    col1,col2 = st.columns(2)

    with col1:

      Button2 = st.button("Modify", use_container_width= True)

    if Button2:

      mydb = sqlite3.connect("Bizcard.db")
      mycursor = mydb.cursor()

      mycursor.execute(f"DELETE FROM Bizcard_details WHERE NAME = '(Select_name)'")
      mydb.commit()

      # Insert query

      insert_query = '''INSERT INTO Bizcard_details(NAME,
                        DESIGNATION,
                        COMPANY_NAME,
                        CONTACT,
                        EMAIL,
                        WEBSITE,
                        ADDRESS,
                        PINCODE,
                        IMAGE
                        )

                        values(?,?,?,?,?,?,?,?,?)'''

      datas = df_4.values.tolist()[0]

      mycursor.execute(insert_query, datas)
      mydb.commit()

      st.success("MODIFIED SUCCESSFULLY")

elif select == "Delete":
  
  mydb = sqlite3.connect("Bizcard.db")
  mycursor = mydb.cursor()

  col1,col2 = st.columns(2)

  with col1:
    #Select query
    select_query_1= "SELECT NAME FROM Bizcard_details"

    mycursor.execute(select_query_1)
    table = mycursor.fetchall()
    mydb.commit()

    name = []

    for i in table:
      name.append (i[0])

    name_select = st.selectbox("Select the name", name)


  with col2:
    #Select query
    select_query_2 = f"SELECT DESIGNATION FROM Bizcard_details WHERE NAME = '{name_select}'"

    mycursor.execute(select_query_2)
    table2 = mycursor.fetchall()
    mydb.commit()

    Designation = []

    for j in table2:
      Designation.append (j[0])

    Designation_select = st.selectbox("Select the Designation", Designation)

  
  if name_select and Designation_select:
    col1,col2,col3 = st.columns(3)

    with col1:
      
      st.write(f"selected Name : {name_select}")
      st.write("")
      st.write("")
      st.write("")
      st.write(f"Selected Designation : {Designation_select}")

    with col2:

      st.write("")
      st.write("")
      st.write("")
      st.write("")

      remove = st.button("Delete", use_container_width= True)

      if remove:

        mycursor.execute(f"DELETE FROM Bizcard_details WHERE NAME ='{name_select}' AND DESIGNATION = '{Designation_select}'")
        mydb.commit()

        st.warning("DELETED")

