The Cafe Blog Website allows users to add a cafe, edit or delete a cafe. 
For the backend of the website Flask is predominately utilised to create routes for various routes to webpages. 
SQLite and sqlalchemy is also utilised to create a database storing the users account credentials and the cafe's detials.
When the User creates an account a hash is generated via bcrypt hash function and is also compared when a user is logging.
The front-end of the website utilises flask_bootstrap via Bootstrap5 for the design with CSS added to adjust the layout. 
