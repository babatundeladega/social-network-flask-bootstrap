# Social Network Flask Bootstrap


## Preface
Python's web frameworks (**Bottle**, **Django**, **Flask**, **Tornado**, **Web.py**) power quite a fraction of the world's most visited sites -- [Pinterest](www.pinterest.com), [Reddit](www.reddit.com), [Quora](www.quora.com) & [DropBox](www.dropbox.com) amongst a rather long list. A vast majority of these sites _(including [Instagram](www.instagram.com))_ are built with [Django](www.djangoproject.com) -- because of its batteries included philosophy.

[Instagram](www.instagram.com), founded in 2010 and perhaps the fastest growing social network, most interestingly have their own custom-built version of [Django](www.djangoproject.com) -- which possesses several middlewares they were able to build because of Django's mutability features. Instagram growing to be one of the world's most used social networks, makes me both proud to be a _pythonista_ and slightly envious it wasn't built in [Flask](flask.pocoo.org).

[Flask](flask.pocoo.org) is simple, flexible and has a certain fine-grained control. These peculiar qualities drew me towards it, and made me decide to be Flask ninja. Now, being the ninja I once aspired to be, I set out to build a simple version of **Instagram with all of its signatory features (Stories, Collections, Direct Messaging, etc)**.

So, for all interested in building the next big social network, here is something to get you started.



## Overview
### Resource Hierarchy
+ Apps
    + Users
        + Collections
        + Messages
        + Notifications
        + Posts
            + Comments
            + Likes
        + Stories
        + Users
    
### Authentication
+ **API Keys**: API keys are required to be sent in the `request headers` as the 
value of `api-key` when making requests to an **App**'s child resources 
(ex. Users)

+ **Auth Token**: Tokens are required to be sent in the `request headers` as 
the value of `Authorization` when making requests to a **User**'s child 
resources (ex. Notifications, Messages)

Only one of the above should be sent per request. 

## Usage
This project will be deployed on Heroku later on, so developers would only 
need to integrate with the API, but currently you could
+ Git clone and modify as you wish. *For an out-of-box experience, edit 
only instance/config.py!*
