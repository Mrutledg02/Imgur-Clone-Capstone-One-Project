# Project Proposal

## Get Started

| Description | Fill in |
| ------------ | ------- |
| Tech Stack | Python/Flask, PostgreSQL, SQLAlchemy, Heroku, Jinja, RESTful APIs, JavaScript, HTML, CSS |
| Type | Website |
| Goal | The goal of this project is to create a simplified version of Imgur where users can upload and share images. The website will allow users to register, upload images, view images uploaded by other users, comment on images, and vote on images. It aims to provide a user-friendly platform for sharing and discovering images. |
| Users | The target users of this app are individuals who enjoy sharing and exploring images online. The demographic includes a wide range of age groups and interests, as the platform will cater to various image categories and topics. Users may also include artists and photographers looking to showcase their work to a broader audience. |
| Data | The project will primarily utilize user-generated data, including images uploaded by users, user profiles, comments, and votes on images. Additionally, basic user information such as usernames and passwords will be stored securely. The data will be collected through user interactions with the website's interface and stored in a PostgreSQL database. |

---

# Breaking down your project

When planning your project, break down your project into smaller tasks, knowing that you may not know everything in advance and that these details might change later. Some common tasks might include:

## Task Name: Design Database schema

**Description:** Designing the database schema involves understanding the relationships between different entities such as users, images, comments, and likes. It requires careful consideration of data organization and normalization principles.

---

## Task Name: Source Your Data

**Description:** Utilize PostgreSQL as the primary data source.

---

## Task Name: User Flows

- **Registration and Authentication:** New users should be able to register for an account by providing basic information like username, email, and password. Upon registration, users should be authenticated and logged in automatically. Returning users should be able to log in using their credentials. 

- **Image Upload:** Authenticated users should be able to upload images to the platform. After uploading an image, users should be redirected to view the uploaded image or continue browsing the site.
  
- **Image Viewing:** Users should be able to browse through a feed of images uploaded by other users. Each image should display relevant information such as the uploader's username, upload date, comments, and votes. Users should be able to click on an image to view it in full size and see additional details. 
  
- **Commenting:** Authenticated users should be able to post comments on images. Each image should display existing comments, and users should have the option to add their own comments. 
  
- **Liking:** Users should be able to like on images (thumbs-up or thumbs-down) to indicate their preferences. The total number of likes or dislikes for each image should be displayed alongside the image.
  
- **User Profile:** Users should have a profile page where they can view their uploaded images, comments, and liking history. Users should be able to edit their profile information and settings. 
  
- **Search and Filters:** Users should have the ability to search for specific images or browse images.
  
- **Navigation:** The site should have clear navigation menus and buttons to help users easily move between different sections of the site. Links to popular or trending images could be provided to encourage user engagement.
  
---

## Task Name: Set up backend and database

**Description:** Configure the environmental variables on your framework of choice for development and set up a PostgreSQL database.

---

## Task Name: Set up frontend

**Description:** Set up the frontend framework of choice and link it to the backend with a simple API call.

---

## Task Name: User Authentication

**Description:** Full-stack feature - ability to authenticate (login and sign up) as a user.

---

## Database Schema

### User Model:

- Attributes:
  - User ID (Primary Key)
  - Username
  - Email
  - Password (hashed)
  - Registration Date
  - About
  - Total Views

- Relationships:
  - One-to-many relationship with posts (One user can have multiple uploaded posts)
  - One-to-many relationship with comments (One user can post multiple comments)
  - One-to-many relationship with likes (One user can like multiple posts)

### Post Model:

- Attributes:
  - Post ID (Primary Key)
  - Title
  - Description
  - Image Path
  - Thumbnail
  - Creation Date
  - Views Count
  - Likes Count
  - Dislikes Count

- Relationships:
  - Many-to-one relationship with users (Many posts belong to one user)
  - One-to-many relationship with comments (One post can have multiple comments)
  - One-to-many relationship with likes (One post can have multiple likes)

### Comment Model:

- Attributes:
  - Comment ID (Primary Key)
  - Post ID (Foreign Key referencing the Post Model)
  - User ID (Foreign Key referencing the User Model)
  - Text
  - Creation Date

- Relationships:
  - Many-to-one relationship with users (Many comments belong to one user)
  - Many-to-one relationship with posts (Many comments belong to one post)

### Like Model:

- Attributes:
  - Like ID (Primary Key)
  - Post ID (Foreign Key referencing the Post Model)
  - User ID (Foreign Key referencing the User Model)
  - Like Type (Boolean indicating whether it's a like or dislike)

- Relationships:
  - Many-to-one relationship with users (Many likes belong to one user)
  - Many-to-one relationship with posts (Many likes belong to one post)
  
---

### Source Of Your Data:

User Input: Users can register, log in, and upload images along with descriptions. These inputs are processed and stored in the database.

External APIs: The application makes requests to an external API (https://api.api-ninjas.com/v1/quotes) to fetch random quotes for display on the homepage. These quotes are then integrated into the application.

Database: Using a PostgreSQL database (postgresql:///imgur_clone_db) to store user information, posts (including images and descriptions), comments, likes, and other relevant data.

Here's a breakdown of how these sources are utilized:

Post Uploads: Authenticated users can upload images along with titles and descriptions. These uploads are processed by the application, and the images are stored in the server's file system (UPLOAD_FOLDER). Details about the posts (such as title, description, image path, user ID, etc.) are stored in the database as Post entries.

Random Quotes: The application fetches random quotes from an external API and displays them on the homepage. This adds a dynamic element to the application's content.

Likes, Comments, and Views: Users can interact with posts by liking them, adding comments, and viewing them. These interactions are stored in the database (Post, Like, Comment), allowing the application to keep track of user engagement with posts.

User Profiles: Users have profiles where they can view their uploads, liked posts, comments, and other information. These profiles are dynamically generated based on the data stored in the database.

### Database Creation:

The database itself (imgur_clone_db) needs to be created separately, usually using a PostgreSQL command line interface like psql or a GUI tool like pgAdmin.

Once the database is created, Flask-SQLAlchemy will handle the interactions with it through the application code.

Capstone Example: [Link](https://github.com/hatchways/sb-capstone-example/issues/2) 

Navigation:

The site should have clear navigation menus and buttons to help users easily move between different sections of the site.
Links to popular or trending images could be provided to encourage user engagement.

[Link](https://github.com/hatchways/sb-capstone-example/issues/3)

Set up backend and database:

Configure the environmental variables on your framework of choice for development and set up database. 

[Link](https://github.com/hatchways/sb-capstone-example/issues/4) 

Set up frontend:

Set up frontend framework of choice and link it to the backend with a simple API call for example.

[Link](https://github.com/hatchways/sb-capstone-example/issues/5)

User Authentication:

Fullstack feature - ability to authenticate (login and sign up) as a user 

[Link](https://github.com/hatchways/sb-capstone-example/issues/6)

## Labeling

Labeling is a great way to separate out your tasks and to track progress. Here’s an [example](https://github.com/hatchways/sb-capstone-example/issues) of a list of issues that have labels associated.

| Label Type | Description | Example |
| ----------- | ----------- | ------- |
| Difficulty | Design Database schema - Medium: Designing the database schema involves understanding the relationships between different entities such as users, images, comments, and likes. It requires careful consideration of data organization and normalization principles.

Source Your Data - Easy: If leveraging an external API, this task primarily involves examining the API documentation, comprehending the request methods, and managing the data returned by the API. However, in this case, without utilizing an external API, sourcing data involves internal mechanisms such as form submissions, database interactions, and file uploads.

User Flows - Medium: Designing user flows requires thinking through the various paths users might take within the application. It involves considering usability principles, user interface design, and ensuring a smooth and intuitive experience for users.

Set up backend and database - Medium: Setting up the backend and database involves configuring the development environment, installing necessary dependencies, setting up database connections, and creating API endpoints. It requires familiarity with the chosen tech stack and understanding of server-side development.

Set up frontend - Medium: Setting up the frontend involves selecting and configuring a frontend framework, designing user interfaces, and integrating frontend components with the backend. It requires knowledge of HTML, CSS, and JavaScript.

User Authentication - Medium: Implementing user authentication involves handling user registration, login, session management, and password hashing. It requires understanding security best practices and familiarity with authentication libraries or frameworks.

### Stretch Goals:

You can also label certain tasks as stretch goals - as a nice to have, but not mandatory for completing this project. 
 
Social Features - Implement additional social features such as user following, private messaging between users, and notifications for new comments or votes on uploaded images. (Stretch Goal)

Advanced Image Processing - Integrate image processing functionalities such as cropping, resizing, and applying filters to uploaded images. (Stretch Goal)

Analytics Dashboard - Develop an analytics dashboard for users to track the performance of their uploaded images, including views, likes, and comments. (Stretch Goal)

Tagging System - Implement a tagging system for images to allow users to categorize and search for images based on tags or keywords. (Stretch Goal)

Mobile App Integration - Create a mobile app version of the Imgur clone to provide users with a native mobile experience for browsing and uploading images. (Stretch Goal) | Must Have, Stretch Goal |
