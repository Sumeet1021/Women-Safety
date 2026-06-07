# 🛡️ Women Safety AI System

An AI-powered Women Safety Analysis and Monitoring System built using Flask, Machine Learning, Mongo-style data processing, SQLite, and Interactive Maps. The project analyzes user feedback, predicts sentiment, identifies risk levels, and visualizes safety information for different locations.

---

## 📌 Project Overview

Women Safety AI is designed to help identify potentially unsafe locations through community feedback and AI-based sentiment analysis.

Users can submit safety-related feedback about a location, and the system:

* Analyzes the sentiment of the feedback using Machine Learning
* Classifies locations as Safe, Neutral, or Unsafe
* Calculates risk levels
* Stores reports in a database
* Displays location-based safety insights
* Visualizes safety information on an interactive map

---

## 🚀 Features

### 🤖 AI Sentiment Analysis

* Predicts sentiment from user feedback
* Classifies feedback as:

  * Positive
  * Neutral
  * Negative

### 📍 Location-Based Safety Tracking

* Supports multiple locations
* Uses geographical coordinates
* Maps reports to real-world locations

### 📊 Safety Risk Assessment

* Generates risk scores
* Identifies potentially unsafe areas
* Aggregates community reports

### 🗺️ Interactive Safety Map

* Displays location safety information
* Visualizes sentiment-based safety indicators
* Supports geographical analysis

### 🗄️ Database Integration

* SQLite database storage
* Stores reports and safety information
* Maintains historical records

### 📈 Data Analytics

* Area-wise safety analysis
* Sentiment aggregation
* Community safety insights

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* Flask

### Machine Learning

* Scikit-learn
* Pickle Model
* NLP Preprocessing

### Database

* SQLite

### Data Processing

* Pandas
* NumPy

### APIs & Services

* Geolocation Services
* Interactive Maps

---

## 📂 Project Structure

```bash
women-safety-ai/
│
├── app.py
├── dataset.csv
├── safety_data.db
├── sentiment_model.pkl
├── vectorizer.pkl
├── requirements.txt
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── templates/
    └── index.html
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Sumeet1021/women-safety-ai.git
cd women-safety-ai
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Application

```bash
python app.py
```

Application will run on:

```text
http://localhost:5000
```

---

## API Endpoints

### Home Page

```http
GET /
```

### Predict Sentiment

```http
POST /predict
```

### Submit Feedback

```http
POST /submit-feedback
```

### Map Data

```http
GET /map-data
```

### Location Analytics

```http
GET /get_locations_data
```

### Recent Reports

```http
GET /recent_reports
```

---

## Machine Learning Model

The system uses a trained sentiment analysis model to:

* Clean user text
* Convert text into vectors
* Predict sentiment
* Generate safety insights

Model Files:

```text
sentiment_model.pkl
vectorizer.pkl
```

---

## Applications

* Smart City Safety Monitoring
* Women Safety Awareness
* Community Safety Reporting
* Crime-Prone Area Identification
* Public Safety Research

---

## Future Enhancements

* Emergency SOS Feature
* Real-Time Crime Alerts
* User Authentication
* Mobile Application
* AI Chatbot Assistance
* Live Location Tracking
* Advanced Analytics Dashboard

---

## Author

### Sumeet Gupta

* Artificial Intelligence & Data Science Student
* Machine Learning Enthusiast
* Full Stack Developer

GitHub:
https://github.com/Sumeet1021

---

## License

This project is developed for educational, research, and academic purposes.
