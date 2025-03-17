# How to run the project

1. To start the application execute commands:
    - `git clone https://github.com/tompin/M4.git`
    - `cd M4`
    - `docker compose up -d --build`

2. To stop the application execute commands:
    - `docker compose down`


# Exemplary client (demo)

After starting application, open `frontend/demo.html` in your browser to connect to websocket. After image will be
uploaded, you will see the result in the browser.


# How to upload an image

`curl -X POST -F "image=@/path/to/your/image.jpg" http://localhost:8282/upload-image/`

# Tests

To run tests execute command run in apps folder on backend container:
    - `./manage.py test` 

