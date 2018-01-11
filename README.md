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

## Tutorials used:
I do not speak django or python very well. The majority of my site is based off of the tutorial on
https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Tutorial_local_library_website.
To directly upload to s3, I've mostly followed the guides from heroku on
https://devcenter.heroku.com/articles/s3-upload-python.

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
- [ ] captcha and extra security measurs against bruce forcing robots
- [ ] limit every user to 10000 hands
- [ ] styling

Nice to haves:
- [ ] REST API design
- [ ] payment system for user to buy more hands
- [ ] expanded database design (hand models instead of json object substitutes)

## Database Design
![alt text](https://shielded-basin-59122.herokuapp.com/static/images/current_schema.png)
