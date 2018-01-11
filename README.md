# Mania Hand Converter
This is a website used to convert poker mania hand histories into pokerstars hand histories to import into PokerTracker or HEM.

## Technologies:
- backend
  - Django (see requirements.txt)
- frontend
  - ghetto jquery
  - blueimp's fileupload (to simplify ajax calls)
- hosting
  - heroku (comes with postgres)
  - AWS S3
  
## Check out the site: 
https://shielded-basin-59122.herokuapp.com/
  
## What's done:
- [x] hand history converter
  - [x] multiple file uploads
  - [x] storage to database
- [x] authentication
- [x] storage to s3
- [x] deployed (to heroku)

Todos:
- [ ] slug configuration for item IDs
- [ ] profile page
- [ ] limit every user to 10000 hands
- [ ] styling

Nice to haves:
- [ ] REST API design 
- [ ] payment system for user to buy more hands
