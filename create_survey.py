import streamlit as st
import requests
import json
import re

st.title('Create a survey')
survey_name = st.text_input('Survey name')
survey_description = st.text_input('Survey description')

num_questions = st.number_input('How many questions would you like to add?', min_value=1, max_value=10, step=1)

survey_questions = []
for i in range(1, num_questions+1):
    st.subheader(f'Question {i}')
    question_text = st.text_input(f'Question {i} text')
    subject_1 = st.text_input(f'Subject 1 for Question {i}', key=f'subject_1_{i}')
    subject_2 = st.text_input(f'Subject 2 for Question {i}', key=f'subject_2_{i}')
    survey_questions.append({'subject_1': subject_1, 'subject_2': subject_2, 'question_text': question_text})

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

api_key = 'tfp_6dAxFu9kJnaiiEopwJnnP46w4ki27A8V1eb9aQWSZ77b_3suzqDt6oA79qw'
headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

if st.button('Create Survey'):
    form_fields = []

    # Iterate over the survey questions
    for question in survey_questions:
        subject_ref = question['subject_1'] + question['subject_2']
        subject_ref = subject_ref.replace(' ', '')
        subject_ref = re.sub(r'[^a-zA-Z0-9_]', '_', subject_ref)
        subject_ref = subject_ref.lower()

        form_fields.append({
            "title": f"{question['question_text']}",
            "type": "opinion_scale",
            "ref": subject_ref,
            "properties": {
                "description": "",
                "steps": 10,
                "start_at_one": True,
                "labels": {
                    "left": f"{question['subject_1']}",
                    "center": " ",
                    "right": f"{question['subject_2']}"
                }
            }
        })

    # Merge form fields and settings from sample JSON
    form_data = {
        'title': survey_name,
        'fields': form_fields,
        'settings': {
            'language': 'en',
            'progress_bar': 'proportion',
            'meta': {
                'title': 'Quadrant Quiz',
                'allow_indexing': False,
                'description': 'Strap in for another Quadrant quiz and see where you rank amongst your friends.',
                'image': {
                    'href': 'https://images.typeform.com/images/etHZ54EKCWYL'
                }
            },
            'hide_navigation': False,
            'is_public': True,
            'is_trial': False,
            'show_progress_bar': True,
            'show_typeform_branding': False,
            'are_uploads_public': False,
            'show_time_to_complete': True,
            'show_number_of_submissions': False,
            'show_cookie_consent': False,
            'show_question_number': True,
            'show_key_hint_on_choices': True,
            'autosave_progress': True,
            'free_form_navigation': True,
            'pro_subdomain_enabled': False,
            'capabilities': {
                'e2e_encryption': {
                    'enabled': False,
                    'modifiable': False
                }
            }
        },
        'thankyou_screens': [
            {
                'ref': 'adfac95e-914d-4601-a02b-f2167d08218a',
                'title': 'Got it. Thanks for participating.',
                'type': 'thankyou_screen',
                'properties': {
                    'show_button': False,
                    'share_icons': False,
                    'button_mode': 'default_redirect',
                    'button_text': 'again'
                }
            }
        ],
        'welcome_screens': [
            {
                'ref': '5baf8a10-395f-4380-bc83-aae5a231d68e',
                'title': "You're about to do a Quadrant quiz.",
                'properties': {
                    'show_button': True,
                    'button_text': 'Start',
                    'description': 'Get ready.'
                }
            }
        ],
        'theme': {
            'href': 'https://api.typeform.com/themes/I1Bmr9LW'
        }
    }

    # Make the API request
    response = requests.post('https://api.typeform.com/forms', headers=headers, data=json.dumps(form_data))

    if '_links' in response.json():
        form_url = response.json()['_links']['display']
        form_id = response.json()['id']
        st.success(f'Success! Your survey is available at {form_url}. To view your responses later, put this ID somewhere safe: {form_id}', icon="✅")
    else:
        st.write('Failed to create the survey. Please try again later.')


