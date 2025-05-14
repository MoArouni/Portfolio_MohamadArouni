# Fixing Database Reset Issues in Deployment

This document explains how to prevent your database from being reset every time the application is redeployed or restarted.

## The Problem

When the application starts, it checks if the database needs to be initialized. This initialization creates all the database tables and might insert initial data like admin users. However, in some deployment environments, this initialization runs on every restart, causing:

1. Errors about tables already existing
2. Duplicate key errors when trying to create admin users
3. Loss of data between deployments

## The Solution: SKIP_DB_INIT Environment Variable

The application has been updated to respect a `SKIP_DB_INIT` environment variable. When set to `true`, the application will skip all database initialization steps, assuming the database is already set up.

### How to Set SKIP_DB_INIT

#### On Railway

1. Go to your project dashboard
2. Click on your service (the Flask application)
3. Navigate to "Variables"
4. Add a new variable:
   - Name: `SKIP_DB_INIT`
   - Value: `true`
5. Deploy your application with this variable set

#### On Heroku

Run this command from your terminal:

```bash
heroku config:set SKIP_DB_INIT=true --app YOUR_APP_NAME
```

Replace `YOUR_APP_NAME` with your Heroku app name.

#### Other Platforms

Consult your platform's documentation on how to set environment variables.

## When to Set This Variable

Set the `SKIP_DB_INIT` variable **after** your first successful deployment that initializes the database. The typical workflow is:

1. Deploy the application for the first time **without** `SKIP_DB_INIT` set
2. Verify that the database is correctly initialized (you can create users, posts, etc.)
3. Set the `SKIP_DB_INIT` variable to `true`
4. All subsequent deployments will preserve your database data

## Troubleshooting

If you set `SKIP_DB_INIT=true` but your database wasn't properly initialized, you can:

1. Temporarily remove the `SKIP_DB_INIT` variable
2. Deploy again to allow initialization to run
3. Re-add the `SKIP_DB_INIT` variable after the database is initialized

## Checking the Status

You can check if `SKIP_DB_INIT` is properly set by visiting the `/health` endpoint of your application. It should include `"skip_db_init": true` in the response. 