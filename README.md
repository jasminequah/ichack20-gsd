# Inspiration
When we are travelling or living far away from friends or loved ones, sometimes we just want to imagine being in the same space as them. What if we can play a game in the same 'space' as them, create a combined happy birthday video, or even film a vlog together remotely?

# What it does
We have built a non-conventional video chatting platform to bring the other person to your space. You are able to talk with each other like just any other regular video chatting platform, but you get to see both of you together in the same screen/environment! We also integrated a few interactive games to make the hangout a bit more exciting.

# How we built it
We built the frontend in HTML and vanilla JS, backend in Python and the Flask framework. The WebRTC signalling server is hosted by Scaledrone. The image processing (foreground/background segmentation) is done in python with the OpenCV and TensorFlow Lite libraries.

# Challenges
* Initially we tried using Cisco's Teams Webex SDK/API to facilitate video calls. However, after trying to make it work for our use case (for nearly 8 hours), we decided that it was quite inflexible and not suited to our use case. So we had to quickly find an alternative. We ended up using WebRTC to establish the video call, allowing users to dial into different video rooms through a code.
* Recognizing people in front of a complex background is a difficult task but we didn't need to start from scratch as there are a several semantic image segmentation models publicly available. Most use quite complicated convolutional neural networks and take a long time to run without GPUs. In order to include our segmentation results into a live video feeds, we needed a model that could segment the individual frames in a fraction of a second. Hence, we finally picked a TensorFlow Lite model -- limited documentation made it quite challenging to get started.
* Once we extracted the outline of each of the user's torso/body, we needed to merge them together to form one smooth live stream. This was difficult as we needed a highly efficient algorithm to process large images in real-time. Manipulating and sending videos with different types and formats across different languages was also quite challenging to get right.

# Tech Stack
Python, TensorFlow Lite, OpenCV, Flask, JavaScript, WebRTC

# Accomplishments!
We're happy that we got image segmentation and overlaying live on the video call. We also managed to learn a lot, as none of us had any experience in image segmentation or WebRTC.

# What's next?
We want to have a mobile app to make Stitch Call more accessible, so that you can take your loved ones on the go! We can also definitely improve the efficiency of segmenting and overlaying the images together.

# Setup
### Combined video stream:
Start python HTTP server:
```
python -m http.server
```
Start image processing server:
```
cd image_seg
flask run
```
Open app on localhost (you may need to allow Camera and Microphone permissions) and let someone else connect to it (with the same id)
For example:
1st computer: ```localhost:8000/#ffffff ```
2nd computer: ```146.169.XX.XX:8000/#ffffff```

### Background segmentation demo
```
cd image_seg
python3 seg_demo.py
```
