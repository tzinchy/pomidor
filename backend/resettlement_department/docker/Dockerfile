FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

#set workdir = auth_service
WORKDIR /resettlement_department

# install lib 
COPY requirements.txt /resettlement_department/
RUN pip install -r requirements.txt

# copy to container 
COPY . /resettlement_department/

# PYTHONPATH 
ENV PYTHONPATH=/resettlement_department/app

# Open port
EXPOSE 8001

# For starting app 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]