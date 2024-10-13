# UAV Manufacturing Application

## Login information
- Email: admin@example.com
- Username: admin
- Password: admin
- Admin URL: http://localhost:8000/admin/
- API URL: http://localhost:8000/api/
- Web URL: http://localhost:8000/

## Screenshots
![Screenshot 2024-10-13 at 14 24 28](https://github.com/user-attachments/assets/173e8afb-f38d-47e4-8562-d89211225f5d)

![Screenshot 2024-10-13 at 14 25 25](https://github.com/user-attachments/assets/898b5859-ff02-46fd-9612-0edc5cc1cbed)

![Screenshot 2024-10-13 at 14 26 11](https://github.com/user-attachments/assets/d6b5a1bc-7cd7-4847-b8ad-172101209f09)

![Screenshot 2024-10-13 at 14 26 25](https://github.com/user-attachments/assets/2ccebca6-fc91-4609-9e9b-46ccc8f8a0df)

![Screenshot 2024-10-13 at 14 26 58](https://github.com/user-attachments/assets/d7449cf2-577a-4a52-abbe-cc60f3f3ee94)

![Screenshot 2024-10-13 at 14 27 11](https://github.com/user-attachments/assets/a5368415-0d4d-490e-9f0c-99c61f169836)

![Screenshot 2024-10-13 at 14 38 38](https://github.com/user-attachments/assets/cd07c338-aab7-4108-ad9d-41e275201667)

## Run the application

You must create a superuser before running the application.

```bash
docker-compose build
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate
docker-compose run web python manage.py createsuperuser
docker-compose run web python manage.py collectstatic --noinput
docker-compose up
npm run build
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
