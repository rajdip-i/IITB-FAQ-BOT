FROM python:3-alpine3.15
WORKDIR /chatbot
COPY . /chatbot
RUN pip install -r requirements.txt
EXPOSE 3000
ENV HUGGINGFACEHUB_API_TOKEN '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'
CMD python ./app.py


