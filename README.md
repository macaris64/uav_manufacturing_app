# UAV Manufacturing Application

## Login information
- Email: admin@example.com
- Username: admin
- Password: admin
- Admin URL: http://localhost:8000/admin/
- API URL: http://localhost:8000/api/

## Run the application
```bash
docker-compose up
```

## Migrate the database
```bash
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate
```

## Run all tests
```bash
docker-compose run web python manage.py test manufacturing.tests
```

## Run specific tests
```bash
docker-compose run web python manage.py test manufacturing.tests.test_models
```

## Coverage
```bash
docker-compose run web coverage run --source='.' manage.py test manufacturing.tests
docker-compose run web coverage report
docker-compose run web coverage html
```

## Create a Superuser
```bash
docker-compose run web python manage.py createsuperuser
```
