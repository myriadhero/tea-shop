FROM nginxinc/nginx-unprivileged:alpine

ARG HOSTNAME=localhost

RUN rm /etc/nginx/conf.d/default.conf
COPY nginxcert.key nginxcert.crt /etc/nginx/certs/
COPY default.conf /etc/nginx/conf.d/
RUN sed -i "s/HOSTNAME/${HOSTNAME}/g" /etc/nginx/conf.d/default.conf