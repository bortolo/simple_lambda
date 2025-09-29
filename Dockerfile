# Dockerfile
FROM public.ecr.aws/lambda/python:3.9

# Copia requirements e installa le librerie
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copia il codice della Lambda
COPY . ${LAMBDA_TASK_ROOT}/

# Imposta il handler della Lambda
CMD ["app.lambda_handler"]