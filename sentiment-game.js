document.getElementById("sentiment-game").addEventListener("click", function() {
    runSentimentGame();
})

EXPRESSIONS = ['angry', 'happy', 'sad', 'fearful', 'disgusted', 'neutral']
curr_expression = 0;
leftScore = 0;
rightScore = 0;

async function runSentimentGame() {

    const videoEl = document.getElementById('mergedVideo');

    // if(videoEl.paused || videoEl.ended)
    //   return setTimeout(() => onPlay())
  
    const options = selectedFaceDetector === SSD_MOBILENETV1
          ? new faceapi.SsdMobilenetv1Options({ minConfidence })
          : new faceapi.TinyFaceDetectorOptions({ inputSize, scoreThreshold })
      
    let i = 15;
    while (i >= 0) {
        const result = await faceapi.detectAllFaces(videoEl, options).withFaceExpressions()

        if (result && result.length >= 1) {
            const canvas = document.getElementById("face-rec-overlay");
            const dims = faceapi.matchDimensions(canvas, videoEl, true)
            const resizedResult = faceapi.resizeResults(result, dims)
            const minConfidence = 0.05
            faceapi.draw.drawDetections(canvas, resizedResult)
            faceapi.draw.drawFaceExpressions(canvas, resizedResult, minConfidence)
            
            if (parseFloat(result[0].expressions[EXPRESSIONS[curr_expression]]) > 0.2) {
                if (parseInt(result[0].detection._box._x) < 110) {
                    leftScore++;
                } else {
                    rightScore++;
                }
            }

            if (result.length > 1 && parseFloat(result[1].expressions[EXPRESSIONS[curr_expression]]) > 0.2) {
                if (parseInt(result[1].detection._box._x) < 110) {
                    leftScore++;
                } else {
                    rightScore++;
                }
            }
        }
        i--;
    }
    
    yourScore.innerHTML = "Your score: " + String(leftScore);
    theirScore.innerHTML = "Their score: " + String(rightScore); 
    curr_expression = Math.floor(Math.random() * (EXPRESSIONS.length - 1));
    goalExpression.innerHTML = "Make a " + EXPRESSIONS[curr_expression] + " expression";   
    setTimeout(() => runSentimentGame());
}