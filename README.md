# Imgur Clone

## Overview

This project is an Imgur Clone, a web application inspired by Imgur, a popular online image sharing community. The Imgur Clone allows users to upload images, view images uploaded by other users, leave comments, like/dislike posts, and more.

## Features

- **User Authentication**: Users can sign up for an account, log in, and log out securely.
- **Image Upload**: Authenticated users can upload images to the platform.
- **Image Viewing**: Users can view images uploaded by other users.
- **Comments**: Users can leave comments on images.
- **Likes/Dislikes**: Users can like or dislike images.
- **Profile Pages**: Each user has a profile page where their uploads, total views, and other information are displayed.
- **Search Functionality**: Users can search for images by title or description.
- **Total Views Count**: The platform keeps track of the total views for each user's posts and displays it on their profile page.
- **Responsive Design**: The application is designed to be responsive and accessible on various devices and screen sizes.

## Technologies Used

- **Python/Flask**: Flask is used as the web framework for building the backend of the application.
- **SQLAlchemy**: SQLAlchemy is used as the ORM (Object-Relational Mapping) tool to interact with the PostgreSQL database.
- **PostgreSQL**: PostgreSQL is used as the relational database management system to store user data, images, comments, and other information.
- **HTML/CSS/JavaScript**: Frontend development is done using HTML, CSS, and JavaScript to create the user interface and enhance user experience.
- **Jinja**: Jinja is used as the template engine to render dynamic content in HTML templates.

## Installation

To run the Imgur Clone locally, follow these steps:

1. Clone the repository: `git clone <repository_url>`
2. Navigate to the project directory
3. Install the dependencies: `pip install -r requirements.txt`
4. Set up the PostgreSQL database: `createdb imgur_clone_db;`
5. Run the application: `python3 app.py`
6. Access the application in your web browser at `http://localhost:5000`

## Contributing

Contributions are welcome! If you would like to contribute to the project, please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature-name`
3. Make your changes and commit them: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## Credits

This project was created by [Megan Heinisch]. It was developed as a capstone project for the [Springboard] Software Engineering Bootcamp.