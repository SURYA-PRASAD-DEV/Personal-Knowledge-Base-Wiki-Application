# Personal Knowledge Base / Wiki Application

## Overview

The Personal Knowledge Base / Wiki Application is a full-stack web application designed to help users efficiently organize, manage, and retrieve personal knowledge. Inspired by wiki-based systems, the platform provides a structured environment for creating, editing, categorizing, and searching articles.

The application enables users to build their own knowledge repository, making information management more organized, searchable, and accessible.

---

## Features

* Create, edit, and delete articles
* Organize content using tags and categories
* Internal article linking for easy navigation
* Full-text search functionality
* Article version history tracking
* Responsive and user-friendly interface
* Cloud-based data storage using Firebase Firestore
* Secure and scalable architecture

---

## Tech Stack

### Backend

* Python
* Flask

### Frontend

* HTML5
* CSS3
* Jinja2 Templates

### Database

* Google Firebase Firestore

### Other Tools

* Git
* GitHub

---

## System Architecture

The application follows a Client-Server Architecture:

1. Users interact with the web interface.
2. Flask processes requests and business logic.
3. Firestore stores and retrieves article data.
4. Search and retrieval operations provide quick access to information.
5. Version history maintains article modifications.

---

## Project Structure

```text
Personal-Knowledge-Base-Wiki-Application/
│
├── app.py
├── config.py
├── firestore_db.py
├── requirements.txt
│
├── templates/
│   ├── index.html
│   ├── create_article.html
│   ├── edit_article.html
│   ├── article.html
│   └── search.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── models/
├── services/
└── README.md
```

---

## Key Functionalities

### Article Management

Users can create, edit, update, and delete articles while maintaining a structured knowledge repository.

### Search System

The application provides search capabilities to quickly locate articles based on keywords and content.

### Tagging and Categorization

Articles can be grouped using tags for better organization and navigation.

### Version Tracking

Changes to articles are recorded, enabling users to maintain a history of modifications.

### Internal Linking

Articles can reference other articles, creating a connected knowledge network.

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/Personal-Knowledge-Base-Wiki-Application.git
cd Personal-Knowledge-Base-Wiki-Application
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

### Configure Firebase

1. Create a Firebase project.
2. Enable Firestore Database.
3. Download the Firebase Service Account Key.
4. Place the credentials JSON file in the project directory.
5. Update the configuration settings.

### Run the Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## Learning Outcomes

Through this project, the following concepts were explored:

* Full-Stack Web Development
* Flask Framework
* Firebase Firestore Integration
* Client-Server Architecture
* Database Design
* Search Functionality
* Knowledge Management Systems
* Version Control Concepts
* Scalable Application Development

---

## Future Enhancements

* User Authentication and Authorization
* Rich Text Editor Support
* AI-Based Article Recommendations
* Advanced Search Filters
* Export Articles to PDF
* Collaborative Editing
* REST API Support
* Dark Mode

---

## Conclusion

The Personal Knowledge Base / Wiki Application demonstrates the practical implementation of full-stack web development and cloud database integration. It provides a scalable and user-friendly platform for organizing and managing personal knowledge efficiently while showcasing modern software engineering practices.
