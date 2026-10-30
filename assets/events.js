(() => {
  'use strict';
  const today = () => new Intl.DateTimeFormat('sv-SE', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(new Date());
  function updateStatus() {
    const day = today();
    document.querySelectorAll('.event-node').forEach(node => {
      const state = day < node.dataset.start ? 'upcoming' : day > node.dataset.end ? 'past' : 'current';
      node.dataset.status = state;
      node.querySelector('.event-status').textContent = {upcoming:'即将开始', past:'已结束', current:node.dataset.start === node.dataset.end ? '今日活动' : '进行中'}[state];
    });
  }
  // Photos retain ordinary links when JavaScript is unavailable.
  document.addEventListener('click', event => {
    const link = event.target.closest('.event-image');
    if (!link || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const viewer = document.getElementById('imageViewer');
    const image = document.getElementById('viewerImage');
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    viewer.showModal();
  });
  updateStatus();
  setInterval(updateStatus, 60000);
})();
