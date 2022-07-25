FROM alpine:latest AS build

ADD https://github.com/gohugoio/hugo/releases/download/v0.101.0/hugo_0.101.0_Linux-64bit.tar.gz /tmp

RUN set -ex \
    && tar -xzvf /tmp/hugo_0.101.0_Linux-64bit.tar.gz -C /usr/local/bin/ \
    && rm -rf /tmp/hugo_0.101.0_Linux-64bit.tar.gz \
    && chmod +x /usr/local/bin/hugo

COPY . /tmp/site/
WORKDIR /tmp/site/

RUN set -ex \
    && /usr/local/bin/hugo --theme npe --config=config_en.toml --destination=public/en \
    && /usr/local/bin/hugo --theme npe --config=config.toml --destination=public


FROM nginx:alpine
COPY --from=build /tmp/site/public /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
VOLUME [ "/opt" ]
