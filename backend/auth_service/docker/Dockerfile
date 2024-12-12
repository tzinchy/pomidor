FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

#set workdir = auth_service
WORKDIR /auth_service

# install lib 
COPY requirements.txt /auth_service/
RUN pip install -r requirements.txt

# copy to container 
COPY . /auth_service/

# PYTHONPATH 
ENV PYTHONPATH=/auth_service/app

# Open port
EXPOSE 8000

# For starting app 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
