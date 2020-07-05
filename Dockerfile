FROM python:3.5-alpine

LABEL Name=epubify Version=0.1-beta

WORKDIR /epubify
ADD . /epubify

# Using pip:
RUN python -m pip install -r requirements.txt

CMD ["python", "-m", "epubify", "-cf", "epubify/sample_configs/pocket_articles_to_dropbox.json"]

# Using pipenv:
#RUN python3 -m pip install pipenv
#RUN pipenv install --ignore-pipfile
#CMD ["pipenv", "run", "python3", "-m", "epubify"]

# Using miniconda (make sure to replace 'myenv' w/ your environment name):
#RUN conda env create -f environment.yml
#CMD /bin/bash -c "source activate myenv && python3 -m epubify"
