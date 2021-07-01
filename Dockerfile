FROM python:3.9

ENV PYTHONUNBUFFERED 1
WORKDIR /livechat
COPY requirements.txt /livechat/
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . /livechat/
#COPY entrypoint.sh entrypoint.sh
#RUN chmod +x /livechat/entrypoint.sh
ENV DJANGO_SETTINGS_MODULE=livechat.settings
EXPOSE 8000
EXPOSE 443
#ENTRYPOINT ["entrypoint.sh"]