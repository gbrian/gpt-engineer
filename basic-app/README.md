To build this application, we will need to create several files and directories to structure our project. Here is a list of the core files and directories we will need:

1. Dockerfile: This file will contain the instructions to build our Docker image.
2. docker-compose.yml: This file will define and run our Docker applications with just a single command.
3. package.json: This file will list the packages our project depends on.
4. src/main.js: This is the entry point of our Vue.js application.
5. src/App.vue: This is the main Vue component that will be loaded by main.js.
6. src/components/RegistrationForm.vue: This component will contain the registration form.
7. src/components/Profile.vue: This component will display the user profile.
8. src/components/FriendsList.vue: This component will display the user's friends list.
9. strapi/config/server.js: This file will contain the configuration for our Strapi.js server.
10. strapi/api/user/models/User.settings.json: This file will define the User model for our Strapi.js server.

Now, let's start creating these files:

Dockerfile
