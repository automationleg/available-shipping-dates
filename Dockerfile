FROM python:3.7

ARG username
ARG password
ARG notifip

RUN mkdir /root/.ssh
ADD id_rsa /root/.ssh/
RUN chmod 600 /root/.ssh/id_rsa
 
# We need wget to set up the PPA and xvfb to have a virtual screen and unzip to install the Chromedriver
RUN apt-get install -y wget unzip

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Update the package list and install chrome
RUN apt-get update -y
RUN apt-get install -y google-chrome-stable=89.0.4389.90-1

# Set up Chromedriver Environment variables
ENV CHROMEDRIVER_VERSION 89.0.4389.23
ENV CHROMEDRIVER_DIR /chromedriver
RUN mkdir $CHROMEDRIVER_DIR

# Download and install Chromedriver
RUN wget -q --continue -P $CHROMEDRIVER_DIR "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# Put Chromedriver into the PATH
ENV PATH $CHROMEDRIVER_DIR:$PATH

ADD requirements.txt /
ADD apimarket_schedule.py /
ADD frisco_schedule.py /
ADD check_schedules.py /
ADD browser.py /
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --use-feature=2020-resolver

ENV ARG_USERNAME $username 
ENV ARG_PASSWORD $password 
ENV ARG_NOTIFIP $notifip 

CMD [ "python", "check_schedules.py" ]
