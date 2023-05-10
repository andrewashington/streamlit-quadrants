import streamlit as st
import requests
import json

st.title('Create a survey')
survey_name = st.text_input('Survey name')
survey_description = st.text_input('Survey description')

num_questions = st.number_input('How many questions would you like to add?', min_value=1, max_value=10, step=1)

survey_questions = []
for i in range(1, num_questions+1):
    st.subheader(f'Question {i}')
    subject_1 = st.text_input(f'Subject 1 for question {i}', key=f'subject_1_{i}')
    subject_2 = st.text_input(f'Subject 2 for question {i}', key=f'subject_2_{i}')
    survey_questions.append({'subject_1': subject_1, 'subject_2': subject_2})

survey_data = {'name': survey_name, 'description': survey_description, 'questions': survey_questions}

# Display a preview of the survey in the sidebar
st.sidebar.subheader('Survey Preview')
if survey_name and survey_description:
    st.sidebar.markdown(f'**Name:** {survey_name}')
    st.sidebar.markdown(f'**Description:** {survey_description}')
    if survey_questions:
        for i, question in enumerate(survey_questions):
            st.sidebar.markdown(f'**Question {i+1}:** {question["subject_1"]} vs. {question["subject_2"]}')
else:
    st.sidebar.markdown('Please enter a name and description for your survey.')

# Prepare the data for the API request

survey_data = {'name': survey_name, 'description': survey_description, 'questions': survey_questions}

api_key = 'tfp_ELew6qvpuFvQz2Jg4w3ymCpaUfYDAU2MWjMrZpmn2CMd_3peGwQGv3MzyUK'
headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

if st.button('Create Survey'):
    form_fields = []
    for question in survey_questions:
        form_fields.append({
            'title': f"Rate your preference for {question['subject_1']} vs. {question['subject_2']}",
            'type': 'number',
            'ref': 'subject_rating',
            'properties': {
                'startAtOne': True,
                'minValue': 1,
                'maxValue': 10,
                'steps': 1,
                'required': True
            }
        })

    form_data = {
        'title': survey_name,
        'fields': form_fields
    }

    response = requests.post('https://api.typeform.com/forms', headers=headers, data=json.dumps(form_data))

    if '_links' in response.json():
        form_url = response.json()['_links']['display']
        st.write(f'The form is ready! Click on the link to access it: {form_url}')
    else:
        st.write('Failed to create the survey. Please try again later.')

    st.subheader('API Response')
    st.write(json.dumps(response.json(), indent=4))