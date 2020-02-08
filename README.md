```
npm install --global browserify watchify
npm install
```

Open `public/app.js` with your favourite editor and replace `<insert_your_access_token_here>` on line 3 with your own access token.

Then run:
```
watchify public/app.js -o public/bundle.js -v
```

This will package up all of the dependencies in app.js into a bundle and automatically repeat this whenever app.js changes.

Keep that running and in a separate terminal window run:

```
node server.js
```

