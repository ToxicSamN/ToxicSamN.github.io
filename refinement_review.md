
# Software Engineering/Design
The artifact I have chosen for Software Engineering and Design category came from code written in python for CS-350 Emerging System Architectures and Technologies in February 2021. In this code we were to collect some sensor data and store this data into a JSON file. The program runs at specified intervals to collect the data. My enhancement for this is to increase the complexity and to collect real-time data while also outputting the data to an LCD screen. I will be using a multiprocessor approach to offload the data writing process to its own process while the sensor collecting will continue to run in its own process. This is a best practice approach as data writes are typically a slower process and if collecting real-time data this will need to be offloaded for performance reasons.
This enhancement will demonstrate an ability to use well-founded and innovative techniques, skills, and tools in computing practices for the purpose of implementing computer solutions that deliver value and accomplish industry-specific goals.

# Algorithms and Data Structures
The artifact I have chosen for Software Engineering and Design category came from code written in python for CS-350 Emerging System Architectures and Technologies in February 2021. In this code we were to collect some sensor data and store this data into a JSON file. The program runs at specified intervals to collect the data. As part of my enhancements I am including an LCD screen and will be outputting the temperature and humidity data to the
LCD screen. To accomplish this I need to create a new LCD handler datastructure to control the functionality of the LCD scree, including controlling
the RGB coloring of the background as well as the text output.
This enhancement will accomplish the outcome of design and evaluate computing solutions that solve a given problem using algorithmic principles and computer science practices and standards appropriate to its solution, while managing the trade-offs involved in design choices.

# Databases
The artifact I have chosen for Databases category is coming from code written in python for CS-350 Emerging System Architectures and Technologies in February 2021. In this code we were to collect some sensor data and store this data into a JSON file. However, the correct solution should be to store this data into a database. The enhancement I will be providing here will be to use a Time Series database such as InfluxDB. This can also be achieved with a NoSQL database such as MongoDB. I am choosing to use an InfluxDB database as it is a time series database specifically designed for real-time metric collection. The flow chart of Category one is the same for this category.
This enhancement will accomplish the outcomes of demonstrating an ability to use well-founded and innovative techniques, skills, and tools in computing practices for the purpose of implementing computer solutions that deliver value and accomplish industry-specific goals.

# Code Review
<video width="320" height="240" controls>
<source type="video/mp4" src="https://drive.google.com/file/d/1fvExZ7lUD7lkVA5X-ewyUFkxVZJ_GqLJ/view?usp=sharing">
</video>
