

* lambda depends on two dependencies: healApiPractice and healShared
* add the respective python packages in the requirements.txt file for each dependency
* check in healApiPractice and healShared
* do a ```nano touch_relaod.txt``` on healLambdaApiPractice to trigger a build.
  * Soon will add a trigger to build on checkin for healApiPractice and healShared that will build healLambdaApiPractice
  * without the need for touch_reload.txt
* NEVER edit any aspect of healLambdaApiPractice directly except touch_reload to trigger a build
* It is required to install and run pre-commit hooks for this project.
* No front end component will be added unless there is a postman collection to test the api.  Exceptions is of the front end is mocked
* Every endpoint will have a unit test for CRUD operations

***
## Postman
* for local development with angular and flask, open 2 terminals

```bash
cd heal-angular-practice && ng serve -c local
cd healApiPractice && python3 wsgi.py
```
* unless the need for jwt no need to auth for api testing in postman for local development
* if jwt is needed, heal-practice-development is the auth server to generate tokens
* switch back to heal-practice-local to test locally wth our jwt tokens

## DotEnv

* local all envs in .env file in dot env format outside of git
* No env variables will ever be committed to git


## Flask
* use flask blueprints with FlaskRESTful for all api endpoints
* post, put, patch requests will use json schema validation
* json response pydantic
* If issues with sql Alchemy, refer to @Mikhail Makovenko
