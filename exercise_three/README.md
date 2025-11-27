# Exercise Three: Kubernetes deployments

## Instructions

**Start the services**

```bash
minikube start
```

**Apply the deployments in the right order**

```bash
cd ..
```

```bash
kubectl apply \
    -f rabbitmq-deployment.yaml \
    -f rabbitmq-service.yaml \
    -f env-configmap.yaml
```

**Wait a while**

```bash
kubectl apply \
    -f book-service-deployment.yaml \
    -f book-service-service.yaml \
    -f borrow-service-deployment.yaml \
    -f borrow-service-service.yaml \
    -f database-deployment.yaml \
    -f database-service.yaml \
    -f postgres-data-persistentvolumeclaim.yaml \
    -f user-service-deployment.yaml \
    -f user-service-service.yaml
```

**Setup port forwarding to the 3 services. You have to use 3 different terminals for this**

```bash
kubectl port-forward service/user-service 5002:5002
```

```bash
kubectl port-forward service/book-service 5006:5006
```

```bash
kubectl port-forward service/borrow-service 5003:5003
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
--data '{ ^
    "bookid" : "6", ^
    "author" : "Aravind", ^
    "title" : "Biology" ^
}'
```

5. **Check if the book is added**

```bash
curl --location 'localhost:5006/books/all'
```

6. **Send a borrow request**

```bash
curl --location 'localhost:5002/users/borrow/request' \
--header 'Content-Type: application/json' \
--data '{ ^
    "studentid": "1", ^
    "bookid": "6" ^
}'
```

7. **Check if the borrow request has been processed.**

```bash
curl --location 'localhost:5003/borrow/1'
```
