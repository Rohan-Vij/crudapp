# A Basic CRUD app

I noticed that quite a few hackathon projects use a technology called CRUD - create, read, update, and delete. <br>
Recreating a whole CRUD application each time you make a project can quickly get boring and time intensive. <br>
So, I decided to make a barebones CRUD application which can use store images to help speed up anyone's development time.
<br>

### Environment Variables

Environment variables are used in this project to store the email account (and its credentials) that sends a verification email to users that sign up. <br>
Firstly, you need to allow your Google account (I don't recommend using your personal account for security reasons) access to unescure 3rd-party apps. If you don't know how to do that, reference [this](https://support.google.com/accounts/answer/6010255 "Less secure apps & your Google Account") help center article.
<br>
Once you have allowed 3rd-party apps access to your Google account, create a file called `.env` in the same directory as the other Python files in the app, such as `mongo.py`.
The contents of this file (you can edit it with your IDE) should be something like this (but with your own values):

```
NAME=email_name
DOMAIN=gmail.com
PASSWORD=9rPAhj
```

Make sure the variables `NAME` and `DOMAIN` do not include the "@" sign.