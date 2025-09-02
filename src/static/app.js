let peerConnection;
let webrtc_id;
let isMuted = false;
const audioOutput = document.getElementById('audio-output');
const startButton = document.getElementById('start-button');
const chatMessages = document.getElementById('chat-messages');

let audioLevel = 0;
let animationFrame;
let audioContext, analyser, audioSource;

function updateButtonState() {
    const button = document.getElementById('start-button');
    button.innerHTML = '';

    if (peerConnection && (peerConnection.connectionState === 'connecting' || peerConnection.connectionState === 'new')) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';

        const text = document.createElement('span');
        text.textContent = 'Connecting...';

        button.appendChild(spinner);
        button.appendChild(text);
    } else if (peerConnection && peerConnection.connectionState === 'connected') {
        const pulseCircle = document.createElement('div');
        pulseCircle.className = 'pulse-circle';

        const micIcon = document.createElement('div');
        micIcon.className = 'mute-toggle';
        micIcon.innerHTML = isMuted ? micMutedIconSVG : micIconSVG;
        micIcon.addEventListener('click', toggleMute);

        const text = document.createElement('span');
        text.textContent = 'Stop Conversation';

        button.appendChild(pulseCircle);
        button.appendChild(micIcon);
        button.appendChild(text);
    } else {
        const text = document.createElement('span');
        text.textContent = 'Start Conversation';
        button.appendChild(text);
    }
}

function toggleMute(event) {
    event.stopPropagation();
    if (!peerConnection || peerConnection.connectionState !== 'connected') return;

    isMuted = !isMuted;
    console.log("Mute toggled:", isMuted);

    peerConnection.getSenders().forEach(sender => {
        if (sender.track && sender.track.kind === 'audio') {
            sender.track.enabled = !isMuted;
            console.log(`Audio track ${sender.track.id} enabled: ${!isMuted}`);
        }
    });

    updateButtonState();
}

function setupAudioVisualization(stream) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    audioSource = audioContext.createMediaStreamSource(stream);
    audioSource.connect(analyser);
    analyser.fftSize = 64;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    function updateAudioLevel() {
        analyser.getByteFrequencyData(dataArray);
        const average = Array.from(dataArray).reduce((a, b) => a + b, 0) / dataArray.length;
        audioLevel = average / 255;

        const pulseCircle = document.querySelector('.pulse-circle');
        if (pulseCircle) {
            pulseCircle.style.setProperty('--audio-level', 1 + audioLevel);
        }

        animationFrame = requestAnimationFrame(updateAudioLevel);
    }
    updateAudioLevel();
}

function showError(message) {
    const toast = document.getElementById('error-toast');
    toast.textContent = message;
    toast.style.display = 'block';

    setTimeout(() => {
        toast.style.display = 'none';
    }, 5000);
}

async function setupWebRTC() {
    isConnecting = true;
    const config = __RTC_CONFIGURATION__;
    peerConnection = new RTCPeerConnection(config);

    const timeoutId = setTimeout(() => {
        const toast = document.getElementById('error-toast');
        toast.textContent = "Connection is taking longer than usual. Are you on a VPN?";
        toast.className = 'toast warning';
        toast.style.display = 'block';

        setTimeout(() => {
            toast.style.display = 'none';
        }, 5000);
    }, 5000);

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        setupAudioVisualization(stream);

        stream.getTracks().forEach(track => {
            peerConnection.addTrack(track, stream);
        });

        peerConnection.addEventListener('track', (evt) => {
            if (audioOutput.srcObject !== evt.streams[0]) {
                audioOutput.srcObject = evt.streams[0];
                audioOutput.play();
            }
        });

        peerConnection.onicecandidate = ({ candidate }) => {
            if (candidate) {
                console.debug("Sending ICE candidate", candidate);
                fetch('/webrtc/offer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        candidate: candidate.toJSON(),
                        webrtc_id: webrtc_id,
                        type: "ice-candidate",
                    })
                })
            }
        };

        const dataChannel = peerConnection.createDataChannel('text');
        dataChannel.onmessage = (event) => {
            const eventJson = JSON.parse(event.data);
            if (eventJson.type === "error") {
                showError(eventJson.message);
            }
        };

        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        peerConnection.addEventListener('connectionstatechange', () => {
            console.log('connectionstatechange', peerConnection.connectionState);
            if (peerConnection.connectionState === 'connected') {
                clearTimeout(timeoutId);
                const toast = document.getElementById('error-toast');
                toast.style.display = 'none';
            }
            updateButtonState();
        });

        webrtc_id = Math.random().toString(36).substring(7);

        const response = await fetch('/webrtc/offer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sdp: peerConnection.localDescription.sdp,
                type: peerConnection.localDescription.type,
                webrtc_id: webrtc_id
            })
        });

        const serverResponse = await response.json();

        if (serverResponse.status === 'failed') {
            showError(serverResponse.meta.error === 'concurrency_limit_reached'
                ? `Too many connections. Maximum limit is ${serverResponse.meta.limit}`
                : serverResponse.meta.error);
            stop();
            return;
        }

        await peerConnection.setRemoteDescription(serverResponse);

        const eventSource = new EventSource('/outputs?webrtc_id=' + webrtc_id);
        eventSource.addEventListener("output", (event) => {
            const eventJson = JSON.parse(event.data);
            console.log("Received output event:", eventJson);
            addMessage(eventJson.role, eventJson.content);
        });
    } catch (err) {
        clearTimeout(timeoutId);
        console.error('Error setting up WebRTC:', err);
        showError('Failed to establish connection. Please try again.');
        stop();
    }
}

function addMessage(role, content) {
    const fixedRole = role === "assistant" ? "assistant" : "user";
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', fixedRole);
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function stop() {
    if (animationFrame) {
        cancelAnimationFrame(animationFrame);
    }
    if (audioContext) {
        audioContext.close();
        audioContext = null;
        analyser = null;
        audioSource = null;
    }
    if (peerConnection) {
        if (peerConnection.getTransceivers) {
            peerConnection.getTransceivers().forEach(transceiver => {
                if (transceiver.stop) {
                    transceiver.stop();
                }
            });
        }

        if (peerConnection.getSenders) {
            peerConnection.getSenders().forEach(sender => {
                if (sender.track && sender.track.stop) sender.track.stop();
            });
        }
        console.log('closing');
        peerConnection.close();
    }
    updateButtonState();
    audioLevel = 0;
}

startButton.addEventListener('click', (event) => {
    if (event.target.closest('.mute-toggle')) {
        return;
    }

    console.log('clicked');
    console.log(peerConnection, peerConnection?.connectionState);
    if (!peerConnection || peerConnection.connectionState !== 'connected') {
        setupWebRTC();
    } else {
        console.log('stopping');
        stop();
    }
});