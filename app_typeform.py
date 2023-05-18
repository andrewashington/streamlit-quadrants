import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.offsetbox as mpl_offsetbox
from PIL import Image, ImageDraw
import numpy as np
import base64
import urllib
import os
import sys
import time
import requests
import json
from matplotlib.ticker import MaxNLocator
from PIL import Image, ImageOps, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from collections import defaultdict
from math import pi, cos, sin
import openai


st.title('Quadrants')

st.write("This app uses responses.csv from a Google form and translates it into Quadrants on the fly.")


# Create an input field to get the Typeform Form ID.
api_key = 'tfp_6dAxFu9kJnaiiEopwJnnP46w4ki27A8V1eb9aQWSZ77b_3suzqDt6oA79qw'
openai.api_key = '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'

headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}


if 'typeform_data' not in st.session_state:
    # Create an input field to get the Typeform Form ID.
    form_id = st.text_input('Typeform Form ID', value='', key='form_id', placeholder='Enter your Typeform Form ID here.')
    if st.button('Fetch Data'):
        # First, fetch information about the form so we can get the question titles.
        form_url = f'https://api.typeform.com/forms/{form_id}'
        response = requests.get(form_url, headers=headers)
        if response.status_code == 200:
            # Get the form name
            survey_name = json.loads(response.content)['title']
            # Print the form json to the screen for debugging
            st.write(json.loads(response.content))
            # Get the questions
            survey_questions = json.loads(response.content)['fields']
            # Show a success message with a green check emoji.
            st.success(f'Successfully fetched the data from your survey: {survey_name}.', icon="✅")
            # Create a dictionary of questions and their titles
            questions = {}
            for question in survey_questions:
                questions[question['id']] = question['title']
            # Proceed to fetch the responses
            responses_url = f'https://api.typeform.com/forms/{form_id}/responses'
            response = requests.get(responses_url, headers=headers)
            if response.status_code == 200:
                # Get the responses
                responses = json.loads(response.content)['items']
                # Create a dictionary to store the response data
                response_data = {question['title']: [] for question in survey_questions}
                # Iterate over responses and extract data for each question
                response_data = {}
                for response in responses:
                    for answer in response['answers']:
                        question_id = answer['field']['id']
                        question_title = questions[question_id]
                        if question_title not in response_data:
                            response_data[question_title] = []
                        if answer['type'] == 'text':
                            response_data[question_title].append(answer['text'])
                        elif answer['type'] == 'number':
                            response_data[question_title].append(answer['number'])
                # Create a dataframe with the response data
                typeform_data = pd.DataFrame(response_data)
                st.session_state.typeform_data = typeform_data
                # Show a success message with a green check emoji.
                st.success(f'Successfully fetched your survey responses.', icon="✅")
            else:
                st.write('Failed to fetch the responses. Please try again later.')
        else:
            st.write('Failed to fetch the data. Please try again later.')

        # Create a new dataframe called form_structure
        form_structure = pd.DataFrame(columns=['Title', 'Question ID', 'Right Subject', 'Left Subject'])
        for question in survey_questions:
            # Extract the necessary information for each question
            title = question['title']
            question_id = question['id']
            if 'labels' in question['properties']:
                labels = question['properties']['labels']
                left_subject = labels['left']
                right_subject = labels['right']
            else:
                left_subject = ''
                right_subject = ''
            # Append a new row to the form_structure dataframe
            form_structure = form_structure.append({'Title': title, 'Question ID': question_id,
                                                    'Right Subject': right_subject, 'Left Subject': left_subject},
                                                ignore_index=True)
            st.session_state.form_structure = form_structure
else:
    typeform_data = st.session_state.typeform_data
    form_structure = st.session_state.form_structure        

# Don't display the tabs unless the typeform_data is avaible in the session state

if 'typeform_data' in st.session_state:
    tab1,tab2 = st.tabs(["Compare Questions", "Compare Responses"])
    with tab1: 
        st.subheader("First, select your questions to compare")

        # Filter out 'Name' and 'Timestamp' columns
        columns_to_select = [col for col in typeform_data if col not in ['What is your name?']]

        # Create two columns for the select boxes
        col1, col2 = st.columns(2)
        # Question select
        column_choice1 = col1.selectbox('Select first question', options=columns_to_select)
        column_choice2 = col2.selectbox('Select second question', options=columns_to_select)

        # Display the selected columns
        st.markdown(f"* **You selected {column_choice1} and {column_choice2}**")

        # Look up the Left Subject and Right Subject for both of the selected questions
        left_subject_x = form_structure.loc[form_structure['Title'] == column_choice1, 'Left Subject'].iloc[0]
        right_subject_x = form_structure.loc[form_structure['Title'] == column_choice1, 'Right Subject'].iloc[0]
        left_subject_y = form_structure.loc[form_structure['Title'] == column_choice2, 'Left Subject'].iloc[0]
        right_subject_y = form_structure.loc[form_structure['Title'] == column_choice2, 'Right Subject'].iloc[0]

        # Plot the scatter plot
        fig, ax = plt.subplots()

        x = typeform_data[column_choice1]
        y = typeform_data[column_choice2]

        # Create the scatter plot
        fig, ax = plt.subplots()

        x = typeform_data[column_choice1]
        y = typeform_data[column_choice2]

        scatter = ax.scatter(x, y)

        def process_image(filename):
            img = Image.open(filename).convert("RGBA")  # Ensure the image has an alpha channel

            # Create the mask
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img.size, fill=255)

            # Create a new blank image with a transparent background
            result = Image.new('RGBA', img.size, (0, 0, 0, 0))
            result.paste(img, mask=mask)  # The mask applies to the alpha channel, not the color channels

            result.save(filename, "PNG")  # Save as PNG to preserve transparency

        directory = 'images'
        for filename in os.listdir(directory):
            if filename.endswith('.png'):
                process_image(os.path.join(directory, filename))

        # Group names by their coordinates
        groups = defaultdict(list)
        for i, (x_val, y_val) in enumerate(zip(x, y)):
            groups[(x_val, y_val)].append(typeform_data.loc[i, 'What is your name?'])

        # For each group of names...
        for (x_val, y_val), names in groups.items():
            # ...if there's only one name, plot it directly at the coordinates
            if len(names) == 1:
                img = mpimg.imread(f'images/{names[0]}.png')
                ax.imshow(img, extent=(x_val-0.5, x_val+0.5, y_val-0.5, y_val+0.5), zorder=10, clip_on=False)  # Higher zorder, images will be plotted on top
            # ...if there's more than one name, plot them in a circle around the coordinates
            else:
                for i, name in enumerate(names):
                    angle = 2 * pi * i / len(names)  # compute angle
                    dx, dy = cos(angle) * 0.5, sin(angle) * 0.5  # offset from the center
                    img = mpimg.imread(f'images/{name}.png')
                    ax.imshow(img, extent=((x_val+dx-0.5, x_val+dx+0.5, y_val+dy-0.5, y_val+dy+0.5)), zorder=10, clip_on=False)  # Higher zorder, images will be plotted on top
                    ax.plot([x_val, x_val+dx], [y_val, y_val+dy], color='black')  # line connecting to the center


        # Set integer ticks for x-axis and y-axis
        ax.xaxis.set_ticks(range(1, 11))
        ax.yaxis.set_ticks(range(1, 11))

        # Set label styles for left and right labels
        left_label_style = {'fontsize': 20, 'weight': 'bold', 'color': '#16007a'}
        right_label_style = {'fontsize': 20, 'weight': 'bold', 'color': '#7a0058'}

        # Plot the left subject on the left side of the y-axis
        ax.spines['left'].set_position(('outward', 0))
        left_y_label = ax.set_ylabel(left_subject_y)
        left_y_label.set(**left_label_style)
        left_y_label.set_position((-0.15, 0.5))

        # Plot the right subject on the right side of the y-axis
        ax.spines['right'].set_position(('outward', 0))
        ax2 = ax.twinx()
        ax2.spines['right'].set_position(('outward', 0))
        right_y_label = ax2.set_ylabel(right_subject_y)
        right_y_label.set(**right_label_style)
        right_y_label.set_position((10.5, 5.5))
        ax2.yaxis.set_label_coords(1.15, 0.5)

        # Set label styles for top and bottom labels
        top_label_style = {'fontsize': 20, 'weight': 'bold', 'color': '#0d6244'}
        bottom_label_style = {'fontsize': 20, 'weight': 'bold', 'color': '#05291c'}

        # Plot the left subject on the bottom of the x-axis
        ax.spines['bottom'].set_position(('outward', 0))
        bottom_x_label = ax.set_xlabel(left_subject_x)
        bottom_x_label.set(**bottom_label_style)
        ax.xaxis.set_label_coords(0.5, -0.15)

        # Plot the right subject on the top of the x-axis
        ax.spines['top'].set_position(('outward', 0))
        ax3 = ax.twiny()
        ax3.spines['top'].set_position(('outward', 0))
        top_x_label = ax3.set_xlabel(right_subject_x)
        top_x_label.set(**top_label_style)
        ax3.xaxis.set_label_coords(0.5, 1.15)

        ax.set_aspect('auto')
        ax2.set_aspect('auto')
        ax3.set_aspect('auto')

        # Set x and y axis limits to range from 1 to 10
        ax.set_xlim([1, 10])
        ax.set_ylim([1, 10])
        ax2.set_xlim([1, 10])
        ax2.set_ylim([1, 10])
        ax3.set_xlim([1, 10])
        ax3.set_ylim([1, 10])

        # Add horizontal and vertical lines that intersect at the middle of the scatter plot
        ax.axhline(5.5, color='#dfe1e6', linestyle='--')
        ax.axvline(5.5, color='#dfe1e6', linestyle='--')

        # Render the plot using Matplotlib
        st.pyplot(fig)

        st.subheader("Here's the raw data for that question")
        st.write(typeform_data[['What is your name?', column_choice1, column_choice2]])

    # Group respondents into categories based on favored subjects
    categories = {}

    for index, row in typeform_data.iterrows():
        respondent_name = row['What is your name?']
        response_x = row[column_choice1]
        response_y = row[column_choice2]

        if response_x < 5:
            if response_y < 5:
                category = 'Left/Left'
            elif response_y > 5:
                category = 'Left/Right'
            else:
                category = 'Left/Undecided'
        elif response_x > 5:
            if response_y < 5:
                category = 'Right/Left'
            elif response_y > 5:
                category = 'Right/Right'
            else:
                category = 'Right/Undecided'
        else:
            if response_y < 5:
                category = 'Undecided/Left'
            elif response_y > 5:
                category = 'Undecided/Right'
            else:
                category = 'Undecided/Undecided'

        if category in categories:
            categories[category].append(respondent_name)
        else:
            categories[category] = [respondent_name]
        
    prompt = ""
    for index, row in typeform_data.iterrows():
        respondent_name = row['What is your name?']
        response_x = row[column_choice1]
        response_y = row[column_choice2]

        subject_x = left_subject_x if response_x < 5 else right_subject_x
        subject_y = left_subject_y if response_y < 5 else right_subject_y

        prompt += f"{respondent_name} prefers {subject_x}/{subject_y}. "
    
    st.write(prompt)
    
    # Call the OpenAI API to get ChatGPT's response
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=200,
        temperature=0.7,
        n=1,
        stop=None,
    )

    # Extract and display ChatGPT's response
    chatgpt_response = response.choices[0].text.strip()
    st.write(f"ChatGPT's response: {chatgpt_response}")
    
    with tab2:
        st.title("Tab 2")
        st.write("This is the second tab")
        st.write(form_structure.to_json())

else: 
    st.header("Enter a TypeformID to get started.")





