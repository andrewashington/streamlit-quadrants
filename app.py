import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageDraw
import numpy as np
import base64
import urllib
import os
import sys
import time

st.title('Quadrants')

st.write("This app uses responses.csv from a Google form and translates it into Quadrants on the fly.")


data = pd.read_csv("responses.csv")

# Load the data
data.rename(columns={'WHO TF ARE YOU': 'Name'}, inplace=True)

tab1, tab2, tab3 = st.tabs(["Charts", "Data", "Compatibility"])
chart_container = st.container()

with tab1: 
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

    def getImage(image_path):
        # Load image as RGB
        img = Image.open(image_path).convert("RGB")
        
        # Resize image to (224, 224)
        img = img.resize((224, 224))
        
        # Create circle mask
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
        
        # Create a new image "RGBA" for transparency and paste the image using mask
        result = Image.new("RGBA", img.size)
        result.paste(img, mask=mask)
        
        return result

    # Create a scatter plot using Matplotlib
    fig, ax = plt.subplots()

    # Set the scale of x and y axes
    # Set the scale of x and y axes
    ax.set_xlim([-1, 11])
    ax.set_ylim([-1, 11])


    # Dictionary to store count of occurrences of each data point
    data_point_counts = {}

    # Function to calculate spiral coordinates
    def circle_coords(count, max_images_per_circle=6, image_size=224, zoom_level=0.1):
        import math
        # Image size after zooming
        scaled_image_size = image_size * zoom_level
        # Circle size (distance between images in the circle)
        # Adjust circle_size based on scaled_image_size to prevent overlapping
        circle_size = (scaled_image_size * 1.1) / 72  # 72 is the default DPI for Matplotlib

        # Calculate the number of circles needed based on count and max_images_per_circle
        circle_number = count // max_images_per_circle
        images_in_current_circle = count % max_images_per_circle

        # Calculate angle and radius based on the circle number and images in the current circle
        angle = 2 * math.pi * images_in_current_circle / max_images_per_circle
        radius = circle_size * (circle_number + 1)

        # Calculate x and y offsets
        x_offset = radius * math.cos(angle)
        y_offset = radius * math.sin(angle)
        return x_offset, y_offset


    for i in range(len(data)):
        # Path to the image file
        img_path = f"images/{data['Name'].iat[i]}.png"
        # Load the image
        img = getImage(img_path)

        # Data point
        point = (data[column_choice1].iat[i], data[column_choice2].iat[i])

        # Increment count of this data point
        if point in data_point_counts:
            data_point_counts[point] += 1
        else:
            data_point_counts[point] = 0

        # Create an OffsetImage with adjusted zoom level based on count
        zoom_level = 0.1
        oi = OffsetImage(img, zoom=zoom_level)

        # Calculate offset based on count using circle_coords
        x_offset, y_offset = circle_coords(data_point_counts[point])

        # Create an AnnotationBbox with the OffsetImage, offset by count
        ab = AnnotationBbox(oi, (point[0] + x_offset, point[1] + y_offset), frameon=False)
        ax.add_artist(ab)

    # Draw lines at x=5 and y=5
    ax.axhline(5, color='red')  # horizontal line
    ax.axvline(5, color='red')  # vertical line

    # Set the labels of the x and y axes
    ax.set_xlabel(column_choice1, fontsize='small', labelpad=15, fontweight='bold')
    ax.set_ylabel(column_choice2, fontsize='small', labelpad=15, fontweight='bold')

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

    st.subheader("Here's the raw data for that question")
    st.write(data[['Name', column_choice1, column_choice2]])

data_container = st.container()

with tab2:
    # Show a select box for all the columns in data.
    st.subheader("Select a question to view the data")
    edit_column_choice = st.selectbox('Select a question', options=['Select...'] + list(data.columns))

    # Check if a column has been selected
    if edit_column_choice != 'Select...':
        # After the user has selected a column, show a text_input element where they can edit the value.
        new_column_name = st.text_input("Edit the question name", value=edit_column_choice)

        if st.button('Update Column Name'):
            # Rename the column in the dataframe
            data.rename(columns={edit_column_choice: new_column_name}, inplace=True)

            # Save the dataframe back to the CSV file
            data.to_csv("responses.csv", index=False)

            st.experimental_rerun()  # Refresh the app after the dataframe has been updated
    # Show an expander that hides a table of all the column names.
    with st.expander("View all question names"):
        st.dataframe(data.columns)

    with st.expander("Change a response"):
        modify_response = st.selectbox('Select a question', options=['Select...'] + list(data.columns), key='modify_response')
        # Show a selectbox of unique Name values.
        name_choice = st.selectbox('Select a Name', options=['Select...'] + list(data['Name'].unique()))
        # Show a text_input to edit the response.
        new_response = st.text_input("Edit the response")

        if st.button('Update Response'):
            # Update the response in the dataframe
            data.loc[data['Name'] == name_choice, modify_response] = new_response

            # Save the dataframe back to the CSV file
            data.to_csv("responses.csv", index=False)

            st.experimental_rerun()  # Refresh the app after the dataframe has been updated

    with st.expander("Change a photo"):
        # Show a select box for the user to select a name
        st.subheader("Select a name to update the image")
        name_choice = st.selectbox('Select a name', options=['Select...'] + list(data['Name']))

        # Check if a name has been selected
        if name_choice != 'Select...':
            # Let the user upload an image file
            st.info("Image must be a square PNG file.")
            uploaded_file = st.file_uploader("Choose a square PNG image file", type=['png'])

            if uploaded_file is not None:
                # Open the uploaded image file
                image = Image.open(uploaded_file)

                # Check if the image is square
                if image.size[0] != image.size[1]:
                    st.error("Uploaded image is not square. Please upload a square image.")
                else:
                    # Save the image to the 'images' folder with the same name as the selected name
                    image.save(f"images/{name_choice}.png")

                    st.success(f"Image for {name_choice} has been updated!")
    
with tab3:
    st.subheader(":sparkles: Compatibility Test :sparkles:")
    st.write("Test any 2 names to see just how compatible they are.")
    
    col1, col2 = st.columns(2)
    with col1:
        name1 = st.selectbox('Select a name :cupid:', options=['Select...'] + list(data['Name']), key='name1')
    with col2:
        name2 = st.selectbox('Select a name :cupid:', options=['Select...'] + list(data['Name']), key='name2')

    if st.button('Calculate Compatibility'):

        # Display the calculating spinner
        with st.spinner("Calculating compatibility..."):
            time.sleep(5)

        # Get the responses for the 2 names
        name1_responses = data.loc[data['Name'] == name1].squeeze()
        name2_responses = data.loc[data['Name'] == name2].squeeze()

        # Calculate the compatibility score
        compatibility_score = 0
        for i in range(1, 11):
            try:
                compatibility_score += abs(int(name1_responses[i]) - int(name2_responses[i]))
            except ValueError:
                continue  # Skip this iteration and move to the next one
        
        # Display different messages based on the compatibility score
        if compatibility_score <= 20:
            st.balloons()
            st.success(f"{name1} and {name2} are a perfect match! :heart:")
        elif compatibility_score <= 50:
            st.success(f"{name1} and {name2} are compatible! :heart:")
        elif compatibility_score <= 70:
            st.warning(f"{name1} and {name2} are not very compatible. :broken_heart:")
        else:
            st.error(f"{name1} and {name2} are not compatible at all. :broken_heart:")
        def draw_donut_chart(compatibility_score):
            # Calculate the empty space in the donut
            empty_space = 100 - compatibility_score

            fig, ax = plt.subplots(figsize=(6, 6))

            # Create a list of colors for the chart
            colors = ['red', 'white']

            # Create a figure and axis
            fig, ax = plt.subplots(figsize=(1, 1))
            ax.axis('equal')

            # Create the donut chart
            wedges, texts, autotexts = ax.pie([compatibility_score, empty_space], 
                                            labels=['', ''], 
                                            colors=colors, 
                                            startangle=90, 
                                            counterclock=False, 
                                            autopct='%1.0f%%',
                                            pctdistance=0.85,
                                            textprops={'color': 'white', 'fontsize': 10, 'fontweight': 'bold'},
                                            wedgeprops=dict(width=0.5, edgecolor='white'))

            # Hide the autotexts
            for autotext in autotexts:
                autotext.set_visible(False)

            # Add a circle to create the hole in the middle of the donut
            centre_circle = plt.Circle((0,0),0.7, fc='white')
            ax.add_artist(centre_circle)

            # Set the title of the chart
            ax.set_title(f"Compatibility: {compatibility_score}%", fontsize=20, fontweight='bold', color='black', pad=20)

            # Remove the axis
            ax.axis('off')
            

            # Display the chart in Streamlit
            st.pyplot(fig)

        # Calculate the compatibility score
        for i in range(1, 11):
            response1 = name1_responses[i]
            response2 = name2_responses[i]
            if isinstance(response1, str) and response1.isdigit() and isinstance(response2, str) and response2.isdigit():
                compatibility_score += abs(int(response1) - int(response2))


        # Calculate the fullness level for the donut chart
        fullness_level = 100 - compatibility_score

        # Display the compatibility score
        st.subheader(f"{name1} and {name2} are {fullness_level}% compatible!")

        # Draw the donut chart
        draw_donut_chart(fullness_level)
