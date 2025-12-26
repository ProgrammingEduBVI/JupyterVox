/**
 * JVox utilities
 */

/**
 *  play sound
 */
// Create a static audio object for playing sound. This is because
// creating an audio object right before playing causes an awkward
// scilence/delay before the screenreading sound.
const audio = new Audio();
let reading_rate = 2; // increasing speech speed.
export async function jvox_speak(audioUrl: string){
    // Extract BASE64 encoded audio bytes, and play the audio
    audio.src = audioUrl;
    audio.playbackRate = reading_rate;

    try {
        await audio.play();
        console.log("Audio playing successfully.");
    } catch (err) {
        console.error("Playback failed. Make sure you've interacted with the page.", err);
    }
}

/**
 * Common function to process JVox server audio response
 * @param response 
 */
export async function jvox_handleAudioResponse(response: Response)
{
    console.debug("JVox audio response:", response);

    // Unpack JSON
    const data = await response.json();

    // Access the speech in text and audio
    const speechText = data.speech;
    const base64Audio = data.audio;

    console.debug("speech text:", speechText);

    // Extract BASE64 encoded audio bytes, and play the audio
    const audioUrl = `data:audio/mpeg;base64,${base64Audio}`;
    jvox_speak(audioUrl);
}