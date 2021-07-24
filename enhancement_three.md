
# Enhancement Three: Databases
The artifact I have chosen for Databases came from code written in 
python for CS-350 Emerging System Architectures and Technologies in February 2021. The original
purpose of this project code was to utilize a RaspberryPi with a GrovePi board connected via the
GPIO connector while utilizing various sensors to collect temperature, humidity, and light data. 
Additionally, the data collected was stored into a JSON file to be read by an HTML dashboard. I
have chosen to enhance this artifact by adding an InfluxDB implementation to write the JSON data
to an InfluxDB database so the data can be read in realtime via a dashboard.

This artifact was chosen as it demonstrates my abilities in Python and my understanding of using 
best practices for developing in Python. I wanted to be able to control my data in a database as
opposed to a file. This provides a way to send the data externally or keep it locally to the
program. To achieve this required teh use of external packages from Influx Data, the creators of
InfluxDB. I was able to implement a single function that accepts the formatted JSON data, 
establishes a client connection to InfluxDB and then write the data to the database. This artifact
showcases my understanding an knowledge of InfluxDB as a database and a database structure as a
time-series database. This requires my knowledge for building the database and the retention 
policies required when building the database. It also allows me to display my ability to understand 
the security considerations of the database with enabling authenticated data read and writes.

The process of enhancing the program from a database perspective was actually quite simple. I
have over five years of industry experience in building and maintaining InfluxDB databases. I have
several projects in my career that utilize an InfluxDB writing implementation using code languages
such as Python, GoLang, and even Powershell. This was easiest and most understood part of my
enhancements and I was glad I could implement my career knowledge here.

Overall, the artifact for Databases was adding an InfluxDB implementation to the code. However,
there were additional enhancements that weren't code based, such as setting up an InfluxDB server,
enabling security controls such as authentication and authorization, and finally validating the code
works as expected with the database system.

### Artifact GitHub Repo
[Enhancement Artifact](https://github.com/ToxicSamN/ToxicSamN.github.io/blob/main/enhancements/SammyShuck__CS499_enhancement.py)
