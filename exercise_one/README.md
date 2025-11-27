# Exercise One: Setup UserService and BookService

## Instructions

1. **Start the services**

```bash
docker compose up --build
```

2. **Add a user**

```bash
curl --location 'localhost:5002/users/add' \
--header 'Content-Type: application/json' \
--data '{
    "studentid": "1",
    "firstname": "Aadhithya",
    "lastname": "Ganesh",
    "email": "Aadhi@gmail.com"
}'
```

3. **Check if the user is added**

```bash
curl --location 'localhost:5002/users/all'
```

4. **Add a book**

```bash
curl --location 'localhost:5006/books/add' \
--header 'Content-Type: application/json' \
--data '{
    "bookid" : "6",
    "author" : "Aravind",
    "title" : "Biology"
}'
```

5. **Check if the book is added**

```bash
curl --location 'localhost:5006/books/all'
```
