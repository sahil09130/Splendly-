// Video modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const howItWorksBtn = document.getElementById('how-it-works-btn');
    const videoModal = document.getElementById('video-modal');
    const videoModalOverlay = document.querySelector('.video-modal-overlay');
    const videoModalClose = document.querySelector('.video-modal-close');
    const videoFrame = document.getElementById('video-frame');
    const videoSrc = 'https://www.youtube.com/embed/jNQXAC9IVRw';

    function openModal() {
        videoModal.classList.add('active');
        videoFrame.src = videoSrc;
    }

    function closeModal() {
        videoModal.classList.remove('active');
        videoFrame.src = '';
    }

    if (howItWorksBtn) {
        howItWorksBtn.addEventListener('click', openModal);
    }

    if (videoModalClose) {
        videoModalClose.addEventListener('click', closeModal);
    }

    if (videoModalOverlay) {
        videoModalOverlay.addEventListener('click', closeModal);
    }
});
