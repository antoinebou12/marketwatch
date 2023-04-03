# Deployment

## Environment variables

MARKETWATCH_USERNAME
MARKETWATCH_PASSWORD
MARKETWATCH_GAME_ID 

## Deploy to Vercel

1. Fork this repository
2. Create a Vercel project and link it to your forked repository
3. Add the following environment variables in your Vercel project settings
4. Deploy the project

https://vercel.com/<YourName>/<ProjectName>/settings/environment-variables

## Deploy to Heroku

1. Create a Heroku application via the Heroku CLI or Heroku Dashboard
2. Connect the app with your GitHub repository and enable automatic builds
3. After the build is completed, start the Flask server by executing `heroku ps:scale web=1`
4. Alternatively, you can click the "Deploy to Heroku" button above to automatically start the deployment process
5. Add the following environment variables to your Heroku application:

[![Marketwatch](https://USER_NAME.vercel.app/api/marketwatch)](https://marketwatch.com/game/{ID})

## Run locally with Docker

1. Install Docker
2. Add the following environment variables
3. Open a terminal in the root folder of the repository and execute:

```bash
docker-compose up -d
```


4. Navigate to `http://localhost:5000/` in your web browser to access the service
5. To stop the service, execute:


```bash
docker-compose down
```


## Customization

### Hide the EQ bar

Remove the `#` in front of `contentBar` in line 81 of the current master to hide the EQ bar when you're not currently playing anything.

### Status String

Add a string saying either "Vibing to:" or "Last seen playing:".

### Change height

Change the `height` to `height + 40` (or whatever margin-top is set to).

### Theme Templates

If you want to change the widget theme, you can do so by changing the `current-theme` property in the `templates.json` file. The available themes are:

- light
- dark

If you wish to customize further, you can add your own customized `marketwatch.html.j2` file to the `templates` folder and add the theme and file name to the `templates` dictionary in the `templates.json` file.


