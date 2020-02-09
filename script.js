var merger = new VideoStreamMerger();
merger.start();

if (!location.hash) {
  location.hash = Math.floor(0xFFFFFF).toString(16);
}
const roomHash = 'location.hash.substring(1)';

// TODO: Replace with your own channel ID
const drone = new ScaleDrone('yiS12Ts5RdNhebyM');
// Room name needs to be prefixed with 'observable-'
const roomName = 'observable-' + roomHash;
const configuration = {
  iceServers: [{
    urls: 'stun:stun.l.google.com:19302'
  }]
};
let room;
let pc;


function onSuccess() {};
function onError(error) {
  console.error(error);
};

drone.on('open', error => {
  if (error) {
    return console.error(error);
  }
  room = drone.subscribe(roomName);
  room.on('open', error => {
    if (error) {
      onError(error);
    }
  });
  // We're connected to the room and received an array of 'members'
  // connected to the room (including us). Signaling server is ready.
  room.on('members', members => {
    console.log('MEMBERS', members);
    // If we are the second user to connect to the room we will be creating the offer
    const isOfferer = members.length === 2;
    startWebRTC(isOfferer);
  });
});

// Send signaling data via Scaledrone
function sendMessage(message) {
  drone.publish({
    room: roomName,
    message
  });
}

function startWebRTC(isOfferer) {
  pc = new RTCPeerConnection(configuration);

  // 'onicecandidate' notifies us whenever an ICE agent needs to deliver a
  // message to the other peer through the signaling server
  pc.onicecandidate = event => {
    if (event.candidate) {
      sendMessage({'candidate': event.candidate});
    }
  };

  // If user is offerer let the 'negotiationneeded' event create the offer
  if (isOfferer) {
    pc.onnegotiationneeded = () => {
      pc.createOffer().then(localDescCreated).catch(onError);
    }
  }

  // When a remote stream arrives display it in the #remoteVideo element
  pc.ontrack = event => {
    const stream = event.streams[0];
    merger.addStream(stream, {
      draw: mergeStreams,
    });

    if (!remoteVideo.srcObject || remoteVideo.srcObject.id !== stream.id) {
      remoteVideo.srcObject = stream;
    }
  };

  const mergeStreams = async (ctx, frame, done) => {
    newCanvas = document.createElement('canvas');
    newCanvas.width = merger.width;
    newCanvas.height = merger.height;
    ctx1 = newCanvas.getContext('2d');
    ctx1.drawImage(frame, 0, 0, merger.width, merger.height);

    newFrame = ctx1.getImageData(0, 0, merger.width, merger.height);
    pixels = newFrame.data;

    const url = 'http://127.0.0.1:5000/segment'

    const data = new FormData();
    data.append('file', pixels);

    oldFrame = ctx.getImageData(0, 0, merger.width, merger.height);
    opixels = oldFrame.data;
    overlay = 0.5

    const processedImage = await fetch(url,
        {
            method: 'POST',
            body: data
        }).then(response => {
          if (!response) return null;
          return response.json()

        }).then(data => {
          if (data.status === '500') {
            done();
            return;
          };
          person = JSON.parse(data['file']);
          for (let i = 0; i < opixels.length; i += 4) {
            if (parseInt(person[i/4]) !== 0) {
              opixels[i] = pixels[i];
              opixels[i+1] = pixels[i+1];
              opixels[i+2] = pixels[i+2];
            }
          }
          ctx.putImageData(oldFrame, 0, 0);
          done();
        });
  }

  navigator.mediaDevices.getUserMedia({
    audio: true,
    video: true,
  }).then(stream => {
    // Display your local video in #localVideo element
    localVideo.srcObject = stream;
    merger.addStream(stream, {
      x: 0,
      y: 0,
      width: merger.width,
      height: merger.height,
      mute: false
    });
    mergedVideo.srcObject = merger.result;
    // Add your stream to be sent to the conneting peer
    stream.getTracks().forEach(track => pc.addTrack(track, stream));
  }, onError);

  // Listen to signaling data from Scaledrone
  room.on('data', (message, client) => {
    // Message was sent by us
    if (client.id === drone.clientId) {
      return;
    }

    if (message.sdp) {
      // This is called after receiving an offer or answer from another peer
      pc.setRemoteDescription(new RTCSessionDescription(message.sdp), () => {
        // When receiving an offer lets answer it
        if (pc.remoteDescription.type === 'offer') {
          pc.createAnswer().then(localDescCreated).catch(onError);
        }
      }, onError);
    } else if (message.candidate) {
      // Add the new ICE candidate to our connections remote description
      pc.addIceCandidate(
        new RTCIceCandidate(message.candidate), onSuccess, onError
      );
    }
  });
}

function getBase64Image(imgElem) {
// imgElem must be on the same server otherwise a cross-origin error will be thrown "SECURITY_ERR: DOM Exception 18"
    var canvas = document.createElement("canvas");
    canvas.width = imgElem.clientWidth;
    canvas.height = imgElem.clientHeight;
    var ctx = canvas.getContext("2d");
    ctx.drawImage(imgElem, 0, 0);
    var dataURL = canvas.toDataURL("image/png");
    return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
  }

function localDescCreated(desc) {
  pc.setLocalDescription(
    desc,
    () => sendMessage({'sdp': pc.localDescription}),
    onError
  );
}
