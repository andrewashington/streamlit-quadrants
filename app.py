import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import numpy as np
import base64
import urllib
import os


st.title('Quadrants')

st.write("This app uses responses.csv from a Google form and translates it into Quadrants on the fly.")

data = pd.read_csv('responses.csv')

data.rename(columns={'WHO TF ARE YOU': 'Name'}, inplace=True)

st.subheader("First, select your questions to compare")

# Filter out 'Name' and 'Timestamp' columns
columns_to_select = [col for col in data.columns if col not in ['Name', 'Timestamp']]

# Create two columns for the select boxes
col1, col2 = st.columns(2)

# Question select
column_choice1 = col1.selectbox('Select first question', options=columns_to_select)
column_choice2 = col2.selectbox('Select second question', options=columns_to_select)



# Display the selected columns
st.markdown(f"* **You selected {column_choice1} and {column_choice2}**")


# Function to read image
def getImage(path):
    # Open the image file
    img = Image.open(path)

    # If the image is a png file, convert it to jpg
    if path.endswith('.png'):
        rgb_img = img.convert('RGB')
        rgb_img.save(path[:-4] + '.jpg')
        img = Image.open(path[:-4] + '.jpg')

    # Resize the image
    img = img.resize((20, 20))
    # Convert the image to numpy array
    img = np.array(img)
    # Return the OffsetImage
    return OffsetImage(img)
# Create a scatter plot using Matplotlib
fig, ax = plt.subplots()

# Set the scale of x and y axes
ax.set_xlim([0, 10])
ax.set_ylim([0, 10])

for i in range(len(data)):
    # Path to the image file
    img_path = f"images/{data['Name'].iat[i]}.jpg"
    # Create an AnnotationBbox with the image
    ab = AnnotationBbox(getImage(img_path), (data[column_choice1].iat[i] + 0.5, data[column_choice2].iat[i] + 0.5), frameon=False)
    ax.add_artist(ab)

# Draw lines at x=5 and y=5
ax.axhline(5, color='red')  # horizontal line
ax.axvline(5, color='red')  # vertical line

# Set the labels of the x and y axes
ax.set_xlabel(column_choice1, fontsize='small', labelpad=15)
ax.set_ylabel(column_choice2, fontsize='small', labelpad=15)

ax.xaxis.tick_top()
ax.xaxis.set_label_position('top') 

ax.yaxis.tick_right()
ax.yaxis.set_label_position('right') 

# Add labels to the bottom and left of the plot
ax.xaxis.tick_bottom()
ax.xaxis.set_label_position('bottom') 

ax.yaxis.tick_left()
ax.yaxis.set_label_position('left') 

# Draw dotted lines for each value
for i in range(1, 11):
    ax.axhline(i, color='gray', linewidth=0.5, linestyle='dotted')
    ax.axvline(i, color='gray', linewidth=0.5, linestyle='dotted')


# Create the filename with the selected column names
filename = f"scatterplot_{column_choice1[:4]}_{column_choice2[:4]}.png"

def get_image_download_link(img_path, filename):
    with open(img_path, 'rb') as f:
        image = f.read()

    b64 = base64.b64encode(image).decode()
    href = f'<a download="{filename}" href="data:file/png;base64,{b64}">Download this chart!</a>'

    return href

# Display the plot in Streamlit
st.pyplot(fig)

# Save the plot as an image with the filename
fig.savefig(filename)

# Create a download link for the image
st.markdown(get_image_download_link(filename, filename), unsafe_allow_html=True)

# Delete the saved image file
os.remove(filename)