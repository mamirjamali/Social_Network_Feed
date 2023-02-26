server {
    lisetn ${LISTEN_PORT};

    loaction /static {
        alias /vol/static;
    }

    loaction / {
        uwsgi_pass                ${APP_HOST}:${APP_PORT};
        include                   /etc/nginx/uwsgi_params;
        client_max_body_size      10M;
    }
}