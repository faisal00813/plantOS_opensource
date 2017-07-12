plantOS
============================
Digitizing Agriculture

<a href="https://twitter.com/plant_os"><img height="100" width="150" src="http://logok.org/wp-content/uploads/2014/08/Twitter-logo-bird_logo_2012.png" /></a>
<a href="https://plant-os.com"><img height="80" width="170" src="https://static1.squarespace.com/static/56dc4a48ab48defc35729f22/t/5963ce51414fb5dacb18108d/1499811877062" /></a>
<BR>

<u>Plant OS Components</u>
1. Computer
2. NDVI Camera
3. Data Processing Engine
4. App Engine Analytics
<BR>
1. Computer
<img height="180" width="280" src="https://static1.squarespace.com/static/56dc4a48ab48defc35729f22/t/596446e159cc684e82642d3e/1499744013803/image+%281%29.png?format=500w" />

Our Plant OS computer comprises of a Raspberry Pi 3 Model B and a Plant OS Shield designed with signal isolation and robust number of digital pins to support sensors integrated:
<ul style="list-style-type:circle">
<li>Ambient Temperature</li>
<li>Ambient Humidity</li>
<li>pH</li>
<li>Electrical Conductivity</li>
<li>Total Dissolved Solids</li>
<li>Salinity</li>
<li>Gravity</li>
<li>Soluble Temperature</li>
<li>Light Intensity</li>
</ul>

2. NDVI Camera

<img height="100" width="150" src="https://static1.squarespace.com/static/56dc4a48ab48defc35729f22/t/596448c2e4fcb58b9fb00881/1499744476763/" />
<img height="80" width="170" src="https://static1.squarespace.com/static/56dc4a48ab48defc35729f22/t/596448a36b8f5b325325c2b7/1499744437443" />
<BR>
<img height="180" width="280" src="https://static1.squarespace.com/static/56dc4a48ab48defc35729f22/t/596448c2e4fcb58b9fb00881/1499744476763" />
<BR>

The NDVI camera utilises inexpensive Raspberry Pi No Infrared camera with Sony IMX219 8-megapixel sensor to generate visual analytics including NDVI and plant phenotype analysis with our own object detection. We have developed our own chip to convert video data over conventional HDMI to extend range.

3. Data Processing Engine

Data Processing Engine(DPE) receives streaming data from plantOS computers deployed and processes it through pipelines. Real-Time streaming data runs through the various processing jobs and generates data that is analysed to gain insights on plant growth. DPE is build on Google Cloud Components such as Google Pub/Sub, Dataflow Engine, BigQuery and Google App Engine, to process the data inorder generate timely insights which would be helpful for monitering various factors related to plant growth.

4. App Engine Analytics

<img height="180" width="280" 
src="https://static1.squarespace.com/static/56dc4a48ab48defc35729f22/t/59644426ff7c5099c12c5864/1499743282386/?format=750w" />
<BR>

App Engine Analytics is a unified interface for beginers exploring their plants with real time analytics and for plant scientists to optimize algorithms through a Jupyter notebook configured with plant phenotics and digital plant recipes in collaboration with MIT Media Lab Open Agriculture Initiative (OpenAg).

Partners
============================
<a href="https://www.media.mit.edu/groups/open-agriculture-openag/overview/"><img height="100" width="380" src="https://cdn-business.discourse.org/uploads/mit/original/1X/47f2561abc542873e69b72315981cb3b31e0f6c5.png" /></a>
MIT Media Lab Open Agriculture Initiative (OpenAg)
<BR>
<a href="https://cloud.google.com"><img height="100" width="380" src="https://cloud.google.com/_static/30ed6e856d/images/cloud/gcp-logo.svg" /></a>
Plant OS is powered by Google Cloud Platform
<BR>


