let saveTimer;
function saveAnswer(question, value) {
  const status = document.getElementById('save-status');
  clearTimeout(saveTimer);
  status.innerText = 'Saving...';
  status.style.display = 'block';

  saveTimer = setTimeout(() => {
    fetch('/api/save-answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, answer: value })
    })
    .then(() => { status.innerText = 'Saved!'; })
    .catch(() => { status.innerText = 'Error'; })
    .finally(() => {
      setTimeout(() => status.style.display = 'none', 2000);
    });
  }, 800);
}

function exportData(subject) {
  fetch(`/api/export/${subject}`)
    .then(r => r.json())
    .then(data => {
      const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `${subject}_with_answers.json`; a.click();
    });
}
