document.getElementById("2d-game").addEventListener("click", function() {
    run2DGame();
})

var canvas = document.getElementById("2d-game-canvas");
var ctx = canvas.getContext("2d");
var player1 = document.getElementById('localVideo');

var x,y;
var dx = 2;
var dy = -2;
var ballRadius = 10;
var paddleHeight = 10;
var paddleWidth = 75;
var paddleX = (canvas.width-paddleWidth)/2;
var moveLeft = false;
var moveRight = false;

// Face recognition
const videoEl = document.getElementById('mergedVideo');
const options = selectedFaceDetector === SSD_MOBILENETV1
? new faceapi.SsdMobilenetv1Options({ minConfidence })
: new faceapi.TinyFaceDetectorOptions({ inputSize, scoreThreshold });

async function run2DGame() {
    // Load assets

    x = canvas.width / 2;
    y = canvas.height - 30;

    // Execute draw() every 30ms
    setInterval(draw, 15);
}

function drawBall() {
    ctx.beginPath();
    ctx.arc(x, y, ballRadius, 0, Math.PI * 2);
    ctx.fillStyle="#000000"
    ctx.fill();
    ctx.closePath();
}

function drawPaddle() {
    ctx.beginPath();
    ctx.rect(paddleX, canvas.height-paddleHeight, paddleWidth, paddleHeight);
    ctx.fillStyle = "#0095DD";
    ctx.fill();
    ctx.closePath();
}

function checkMove(face) {
    moveLeft = false;
    moveRight = false;
    if (face[0] && face[0].detection && face[0].detection.box) {
        var box = face[0].detection.box;
        if (box.x > 60) {
            // Video input is flipped
            moveLeft = true;
            console.log("Moving left!");
        } else if (box.x < 35) {
            moveRight = true;
            console.log("Moving right!");
        }
    }
}

async function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawBall();
    drawPaddle();

    if(x + dx > canvas.width-ballRadius || x + dx < ballRadius) {
        dx = -dx;
    }
    if(y + dy > canvas.height-ballRadius || y + dy < ballRadius) {
        dy = -dy;
    }

    const face = await faceapi.detectAllFaces(videoEl, options).withFaceExpressions();
    checkMove(face);
    if(moveLeft) {
        paddleX -= 10;
        if (paddleX < 0){
            paddleX = 0;
        }
    }
    else if(moveRight) {
        paddleX += 10;
        if (paddleX + paddleWidth > canvas.width){
            paddleX = canvas.width - paddleWidth;
        }
    }

    x += dx;
    y += dy;
    // ctx.clip();
    // ctx.drawImage(player1, 0, 0);
}
