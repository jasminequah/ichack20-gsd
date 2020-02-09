document.getElementById("2d-game").addEventListener("click", function() {
    yourScore.innerHTML = "Your score: 0"
    theirScore.innerHTML = "Their score: 0"
    goalExpression.innerHTML = ""
    run2DGame();
})

var canvas = document.getElementById("2d-game-canvas");
var ctx = canvas.getContext("2d");

var x,y;
var dx = 2;
var dy = -2;
var ballRadius = 10;
var paddleHeight = 10;
var paddleWidth = 75;
var p1PaddleX = (canvas.width-paddleWidth)/2;
var p1MoveLeft = false;
var p1MoveRight = false;
var p2PaddleX = (canvas.width-paddleWidth)/2;
var p2MoveLeft = false;
var p2MoveRight = false;
var leftScore = 0;
var rightScore = 0;

// Face recognition
const videoEl = document.getElementById('mergedVideo');
const options = selectedFaceDetector === SSD_MOBILENETV1
? new faceapi.SsdMobilenetv1Options({ minConfidence })
: new faceapi.TinyFaceDetectorOptions({ inputSize, scoreThreshold });

function run2DGame() {
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
    ctx.rect(p1PaddleX, canvas.height-paddleHeight, paddleWidth, paddleHeight);
    ctx.fillStyle = "#0095DD";
    ctx.fill();
    ctx.closePath();

    ctx.beginPath();
    ctx.rect(p2PaddleX, 0, paddleWidth, paddleHeight);
    ctx.fillStyle = "#0095DD";
    ctx.fill();
    ctx.closePath();
}

function checkMove(faces) {
    p1MoveLeft = false;
    p1MoveRight = false;
    p2MoveLeft = false;
    p2MoveRight = false;
    var leftBox;
    var rightBox;
    // I haven't slept for 24 hours I am sorry for this code
    if (faces[0] && faces[0].detection.box) {
        if (faces[1] && faces[1].detection.box) {
            if (faces[1].detection.box.x < faces[0].detection.box.x) {
                // Second face detected is to left of first
                leftBox = faces[1].detection.box;
                rightBox = faces[0].detection.box;
            } else {
                rightBox = faces[1].detection.box;
                leftBox = faces[0].detection.box;
            }
        } else {
            if (faces[0].detection.box.x < 100) {
                leftBox = faces[0].detection.box;
            } else {
                rightBox = faces[0].detection.box;
            }
        }
    }
    if (leftBox) {
        if (leftBox.x > 50) {
            // Video input is flipped
            p1MoveLeft = true;
            console.log("Moving left!");
        } else if (leftBox.x < 40) {
            p1MoveRight = true;
            console.log("Moving right!");
        }
    }
    if (rightBox) {
        if (rightBox.x > 350) {
            p2MoveLeft = true;
            console.log("Moving left!");
        } else if (rightBox.x < 240) {
            p2MoveRight = true;
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
    if(y + dy < ballRadius) {
        if(x > p2PaddleX && x < p2PaddleX + paddleWidth) {
            dy = -dy;
        }
        else {
            console.log("GAME OVER!!!!");
            leftScore++;
            yourScore.innerHTML = "Your score: " + String(leftScore);

            x = canvas.width / 2;
            y = canvas.height - 30;
        }
    }
    else if(y + dy > canvas.height-ballRadius) {
        if(x > p1PaddleX && x < p1PaddleX + paddleWidth) {
            dy = -dy;
        }
        else {
            console.log("GAME OVER!!!!");
            rightScore++;
            theirScore.innerHTML = "Their score: " + String(rightScore);

            x = canvas.width / 2;
            y = canvas.height - 30;
        }
    }

    const faces = await faceapi.detectAllFaces(videoEl, options).withFaceExpressions();
    checkMove(faces);
    if(p1MoveLeft) {
        p1PaddleX -= 10;
        if (p1PaddleX < 0){
            p1PaddleX = 0;
        }
    }
    else if(p1MoveRight) {
        p1PaddleX += 10;
        if (p1PaddleX + paddleWidth > canvas.width){
            p1PaddleX = canvas.width - paddleWidth;
        }
    }
    if(p2MoveLeft) {
        p2PaddleX -= 10;
        if (p2PaddleX < 0){
            p2PaddleX = 0;
        }
    }
    else if(p2MoveRight) {
        p2PaddleX += 10;
        if (p2PaddleX + paddleWidth > canvas.width){
            p2PaddleX = canvas.width - paddleWidth;
        }
    }

    x += dx;
    y += dy;
    // ctx.clip();
    // ctx.drawImage(player1, 0, 0);
}
