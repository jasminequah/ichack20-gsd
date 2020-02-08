const Webex = require('webex');

const accessToken = 'ZWRjM2RhNGEtZmE4Ny00ZTg3LWI3NTgtN2U4MjBlMGQ1OGRhYjRiZGExZjctYTA3_PF84_1b1196c3-dcba-4ea0-ad0d-6aabb5e49fdb';

if (accessToken === '<insert_your_access_token_here>') {
  alert('Please add your access token to app.js');
}

let webex = Webex.init({
  credentials: {
    access_token: accessToken
  }
});

// First, let's wire our form fields up to localStorage so we don't have to
// retype things everytime we reload the page.

[
  'access-token',
  'invitee'
].forEach((id) => {
  const el = document.getElementById(id);

  el.value = localStorage.getItem(id);
  el.addEventListener('change', (event) => {
    localStorage.setItem(id, event.target.value);
  });
});

// There's a few different events that'll let us know we should initialize
// Webex and start listening for incoming calls, so we'll wrap a few things
// up in a function.
function connect() {
  return new Promise((resolve) => {
    if (!webex) {
      // eslint-disable-next-line no-multi-assign
      webex = window.webex = Webex.init({
        config: {
          meetings: {
            deviceType: 'WEB'
          }
          // Any other sdk config we need
        },
        credentials: {
          access_token: document.getElementById('access-token').value
        }
      });
    }

    // Listen for added meetings
    webex.meetings.on('meeting:added', (addedMeetingEvent) => {
      if (addedMeetingEvent.type === 'INCOMING') {
        const addedMeeting = addedMeetingEvent.meeting;

        // Acknowledge to the server that we received the call on our device
        addedMeeting.acknowledge(addedMeetingEvent.type)
          .then(() => {
            if (confirm('Answer incoming call')) {
              joinMeeting(addedMeeting);
              bindMeetingEvents(addedMeeting);
            }
            else {
              addedMeeting.decline();
            }
          });
      }
    });

    // Register our device with Webex cloud
    if (!webex.meetings.registered) {
      webex.meetings.register()
        // Sync our meetings with existing meetings on the server
        .then(() => webex.meetings.syncMeetings())
        .then(() => {
          // This is just a little helper for our selenium tests and doesn't
          // really matter for the example
          document.body.classList.add('listening');
          document.getElementById('connection-status').innerHTML = 'connected';
          // Our device is now connected
          resolve();
        })
        // This is a terrible way to handle errors, but anything more specific is
        // going to depend a lot on your app
        .catch((err) => {
          console.error(err);
          // we'll rethrow here since we didn't really *handle* the error, we just
          // reported it
          throw err;
        });
    }
    else {
      // Device was already connected
      resolve();
    }
  });
}

// Similarly, there are a few different ways we'll get a meeting Object, so let's
// put meeting handling inside its own function.
function bindMeetingEvents(meeting) {
  console.log("bind meeting called")
  // call is a call instance, not a promise, so to know if things break,
  // we'll need to listen for the error event. Again, this is a rather naive
  // handler.
  meeting.on('error', (err) => {
    console.error(err);
  });

  // Handle media streams changes to ready state
  meeting.on('media:ready', (media) => {
    if (!media) {
      return;
    }
    if (media.type === 'local') {
      document.getElementById('self-view').srcObject = media.stream;
      setUpAudioVisualisation(media.stream)
    }
    if (media.type === 'remoteVideo') {
      document.getElementById('remote-view-video').srcObject = media.stream;
    }
    if (media.type === 'remoteAudio') {
      document.getElementById('remote-view-audio').srcObject = media.stream;
      // setUpAudioVisualisation(media.stream)
      greyscaleVideoProcessor.start()
    }
  });

  // Handle media streams stopping
  meeting.on('media:stopped', (media) => {
    // Remove media streams
    if (media.type === 'local') {
      document.getElementById('self-view').srcObject = null;
    }
    if (media.type === 'remoteVideo') {
      document.getElementById('remote-view-video').srcObject = null;
    }
    if (media.type === 'remoteAudio') {
      document.getElementById('remote-view-audio').srcObject = null;
    }
  });

  // Update participant info
  meeting.members.on('members:update', (delta) => {
    const {full: membersData} = delta;
    const memberIDs = Object.keys(membersData);

    memberIDs.forEach((memberID) => {
      const memberObject = membersData[memberID];

      // Devices are listed in the memberships object.
      // We are not concerned with them in this demo
      if (memberObject.isUser) {
        if (memberObject.isSelf) {
          document.getElementById('call-status-local').innerHTML = memberObject.status;
        }
        else {
          document.getElementById('call-status-remote').innerHTML = memberObject.status;
        }
      }
    });
  });

  // Of course, we'd also like to be able to end the call:
  document.getElementById('hangup').addEventListener('click', () => {
    meeting.leave();
  });
}

// Join the meeting and add media
function joinMeeting(meeting) {
  // Get constraints
  const constraints = {
    audio: document.getElementById('constraints-audio').checked,
    video: document.getElementById('constraints-video').checked
  };

  return meeting.join().then(() => {
    const mediaSettings = {
      receiveVideo: constraints.video,
      receiveAudio: constraints.audio,
      receiveShare: false,
      sendVideo: constraints.video,
      sendAudio: constraints.audio,
      sendShare: false
    };

    return meeting.getMediaStreams(mediaSettings).then((mediaStreams) => {
      const [localStream, localShare] = mediaStreams;

      meeting.addMedia({
        localShare,
        localStream,
        mediaSettings
      });
    });
  });
}

// Now, let's set up incoming call handling
document.getElementById('credentials').addEventListener('submit', (event) => {
  // let's make sure we don't reload the page when we submit the form
  event.preventDefault();

  // The rest of the incoming call setup happens in connect();
  connect();
});

// And finally, let's wire up dialing
document.getElementById('dialer').addEventListener('submit', (event) => {
  // again, we don't want to reload when we try to dial
  event.preventDefault();

  const destination = document.getElementById('invitee').value;

  // we'll use `connect()` (even though we might already be connected or
  // connecting) to make sure we've got a functional webex instance.
  connect()
    .then(() => {
      // Create the meeting
      return webex.meetings.create(destination).then((meeting) => {
        // Call our helper function for binding events to meetings
        bindMeetingEvents(meeting);

        return joinMeeting(meeting);
      });
    })
    .catch((error) => {
      // Report the error
      console.error(error);

      // Implement error handling here
    });
});

async function runFaceRec() {
  // load face detection and face expression recognition models
  await faceapi.loadFaceExpressionModel('/models')
  // await faceapi.nets.ssdMobilenetv1.loadFromUri('/models')
  await faceapi.nets.tinyFaceDetector.loadFromUri('/models')
}

const SSD_MOBILENETV1 = 'ssd_mobilenetv1'
const TINY_FACE_DETECTOR = 'tiny_face_detector'

let selectedFaceDetector = TINY_FACE_DETECTOR

// ssd_mobilenetv1 options
let minConfidence = 0.5

// tiny_face_detector options
let inputSize = 512
let scoreThreshold = 0.5

function getFaceDetectorOptions() {
  return selectedFaceDetector === SSD_MOBILENETV1
    ? new faceapi.SsdMobilenetv1Options({ minConfidence })
    : new faceapi.TinyFaceDetectorOptions({ inputSize, scoreThreshold })
}

async function onPlay() {
  let withBoxes = true

  const videoEl = document.getElementById('remote-view-video');

  if(videoEl.paused || videoEl.ended)
    return setTimeout(() => onPlay())


  const options = getFaceDetectorOptions()

  const ts = Date.now()

  const result = await faceapi.detectSingleFace(videoEl, options).withFaceExpressions()

  if (result) {
    const canvas = document.getElementById("face-rec-overlay");
    const dims = faceapi.matchDimensions(canvas, videoEl, true)

    const resizedResult = faceapi.resizeResults(result, dims)
    const minConfidence = 0.05
    if (withBoxes) {
      faceapi.draw.drawDetections(canvas, resizedResult)
    }
    faceapi.draw.drawFaceExpressions(canvas, resizedResult, minConfidence)
  }

  setTimeout(() => onPlay())
}

document.getElementById('enablefacerec').addEventListener('click', () => {
  runFaceRec().then(() => {
    console.log("Face Rec models loaded\n");
    onPlay();
  }).catch(function(error) {
    console.log("Error loading Face Rec models\n");
    console.error(error.message);
  });
});

document.getElementById('extractlocalframe').addEventListener('click', () => {
  extractAndDownloadFrame('self-view', 'local-frame')
});

document.getElementById('extractremoteframe').addEventListener('click', () => {
  extractAndDownloadFrame('remote-view-video', 'remote-frame')
});

function extractAndDownloadFrame(videoId, filename) {
  var video = document.getElementById(videoId);
  var canvas = document.createElement("canvas");
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  var context = canvas.getContext("2d");
  context.drawImage(video, 0, 0);
  var img = canvas.toDataURL("image/jpeg", 1.0);
  downloadImage(img, filename + '.jpeg');
}

function downloadImage(data, filename) {
  var a = document.createElement('a');
  a.href = data;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
}

function setUpAudioVisualisation(audioStream) {
  var audioCtx = new AudioContext();

  var source = audioCtx.createMediaStreamSource(audioStream);

  var analyser = audioCtx.createAnalyser();
  source.connect(analyser);
  analyser.connect(audioCtx.destination)

  analyser.fftSize = 2048;
  var bufferLength = analyser.frequencyBinCount;
  var dataArray = new Uint8Array(bufferLength);
  analyser.getByteTimeDomainData(dataArray);

  // Get a canvas defined with ID "oscilloscope"
  var canvas = document.getElementById("audio-visualisation-canvas");
  var canvasCtx = canvas.getContext("2d");

  // draw an oscilloscope of the current audio source

  function draw() {

    requestAnimationFrame(draw);

    analyser.getByteTimeDomainData(dataArray);

    canvasCtx.fillStyle = "rgb(200, 200, 200)";
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = "rgb(0, 0, 0)";

    canvasCtx.beginPath();

    var sliceWidth = canvas.width * 1.0 / bufferLength;
    var x = 0;

    for (var i = 0; i < bufferLength; i++) {

      var v = dataArray[i] / 128.0;
      var y = v * canvas.height / 2;

      if (i === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    canvasCtx.lineTo(canvas.width, canvas.height / 2);
    canvasCtx.stroke();
  }

  draw();
}

var greyscaleVideoProcessor = {
  timerCallback: function() {
    if (this.video.paused || this.video.ended) {
      return;
    }
    this.computeFrame();
    var self = this;
    setTimeout(function () {
      self.timerCallback();
    }, 16); // roughly 60 frames per second
  },

  start: function() {
    this.video = document.getElementById("self-view");
    this.c1 = document.getElementById("self-view-canvas");
    this.c1.width = this.video.videoWidth
    this.c1.height = this.video.videoHeight
    this.ctx1 = this.c1.getContext("2d");
    var self = this;
    self.timerCallback();
  },

  computeFrame: function() {
    this.ctx1.drawImage(this.video, 0, 0);
    var frame = this.ctx1.getImageData(0, 0, this.c1.width, this.c1.height);
    var l = frame.data.length / 4;

    for (var i = 0; i < l; i++) {
      var grey = (frame.data[i * 4 + 0] + frame.data[i * 4 + 1] + frame.data[i * 4 + 2]) / 3;

      frame.data[i * 4 + 0] = grey;
      frame.data[i * 4 + 1] = grey;
      frame.data[i * 4 + 2] = grey;
    }
    this.ctx1.putImageData(frame, 0, 0);

    return;
  }
};