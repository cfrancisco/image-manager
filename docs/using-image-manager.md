# Using ImageManager

These instructions are meant for development only. 
They should be run on the repository root and will execute the following:
1. Run the necessary environment(postgres+minio) using docker-compose
2. Build an image based on the current repository
3. Run the application inside docker compose network
4. Run the test application

Obs.: Using the option  ```-v $PWD:/usr/src/app local/imagemanager```
will link the docker image application with the local development code,
any changes in the code will update the application immediately using flask's hot
swap mechanism

On terminal #1:

    docker-compose -f local/compose.yml -p imgm up -d
    docker build -f Dockerfile -t local/imagemanager .
    docker run --rm -it --network imgm_default -p 8000:5000 --network-alias image-manager -v $PWD:/usr/src/app local/imagemanager
    
On terminal #2:
    
    cd tests/
    python3 client.py



Request samples using authorization token as {"service": "mytenant"}:

    curl http://localhost:8000/image -H "Accept: application/json" -H "Authorization: Bearer my.eyJzZXJ2aWNlIjogIm15dGVuYW50In0="


    curl -X POST http://localhost:8000/image/ -H "Accept: application/json" -H "Authorization: Bearer my.eyJzZXJ2aWNlIjogIm15dGVuYW50In0=" -H "Content-Type: application/json"  -d '{"label": "FW_Example","fw_version": "1.0.0", "attrs": [{"label": "mandatory","value": "true"},{"label": "description","value": "description"}]}'


    curl -X DELETE http://localhost:8000/image/<image_id> -H "Accept: application/json" -H "Authorization: Bearer my.eyJzZXJ2aWNlIjogIm15dGVuYW50In0="
 