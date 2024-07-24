import requests

student = {
    "StudentID": 2566.0,
    "Age": 17.0,
    "Gender": 0.0,
    "Ethnicity": 0.0,
    "ParentalEducation": 0.5,
    "StudyTimeWeekly": 0.41918744404386094,
    "Absences": 0.3103448275862069,
    "Tutoring": 0.0,
    "ParentalSupport": 0.75,
    "Extracurricular": 0.0,
    "Sports": 0.0,
    "Music": 0.0,
    "Volunteering": 0.0,
}


url = "http://localhost:9696/predict"
response = requests.post(url, json=student)
print(response)
print(response.json())
