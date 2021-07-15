
# Enhancement One: Software Engineering and Design
The artifact I have chosen for Software Engineering and Design came from code written in 
python for CS-350 Emerging System Architectures and Technologies in February 2021. The original
purpose of this project code was to utilize a RaspberryPi with a GrovePi board connected via the
GPIO connector while utilizing various sensors to collect temperature, humidity, and light data. 
Additionally, the data collected was stored into a JSON file to be read by an HTML dashboard.

This artifact was chosen as it demonstrates my abilities in Python and my understanding of using
best practices for developing in Python. 
I also chose this artifact as I found the different components within this project intriguing. 
I wanted to be able to control and LCD screen so that I could build my own weather station. 
I also wanted to showcase my understanding and abilities to develop a multiprocessing application
which is a common and desirable skill for a developer to have. 

The process of enhancing the program from a software engineering and design perspective was
educational for me.
It wasn't too much of a challenged but sufficiently difficult.
One of the challenges I faced was around the security considerations whereby I am
logging my actions and especially the errors. On the surface this isn't difficult, but then
adding in multi-processing complexities requires the ability to communicate these errors back
to the main program. Additionally, getting the multi-processing interactions and code correctly
implemented was also challenging. Once I figured out the structure it was easy to implement, but
there was a bit of trial an error.

Overall, the artifact for software engineering and design was adding additional complexity to the
program. This was achieved by implementing an LCD implementation so that temperature and
humidity could be displayed on the LCD screen. Additionally, I added the ability to write the
data to an InfluxDB database. This allows me to collect the data in real-time and by utilizing
the multi-processing implementation and separating the collection process from the database
process.

### Artifact GitHub Repo
[Enhancement Artifact](https://github.com/ToxicSamN/ToxicSamN.github.io/blob/main/enhancements/SammyShuck__CS499_enhancement.py)
